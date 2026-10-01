## utils/web_console.py
# 将终端输出实时推流到 Web 页面，并把 input() 交互转换为 Web 按钮应答。
# 用法：
#   import utils.web_console as web_console
#   web_console.install()                 # 尽早调用，接管 stdout/stderr
#   answer = web_console.ask_user("是否继续启动？(y/n)", default="n")
import sys
import json
import time
import queue
import threading
import itertools
from collections import deque


class ConsoleBroker:
    """捕获文本块，保存历史，并向所有 SSE 订阅者广播。"""

    def __init__(self, maxlen=4000):
        self.history = deque(maxlen=maxlen)
        self.listeners = []
        self.lock = threading.Lock()

    def publish(self, text):
        if not text:
            return
        if isinstance(text, bytes):
            text = text.decode("utf-8", errors="replace")
        with self.lock:
            self.history.append(text)
            listeners = list(self.listeners)
        for q in listeners:
            try:
                q.put_nowait(("log", text))
            except queue.Full:
                pass

    def publish_event(self, event, payload):
        with self.lock:
            listeners = list(self.listeners)
        data = json.dumps(payload, ensure_ascii=False)
        for q in listeners:
            try:
                q.put_nowait((event, data))
            except queue.Full:
                pass

    def subscribe(self):
        q = queue.Queue(maxsize=2000)
        with self.lock:
            self.listeners.append(q)
            history = list(self.history)
        return q, history

    def unsubscribe(self, q):
        with self.lock:
            if q in self.listeners:
                self.listeners.remove(q)


class PromptManager:
    """把 input() 问答转成 Web 可应答的提示；支持终端与网页双通道，先到先得。"""

    def __init__(self, broker):
        self.broker = broker
        self.cond = threading.Condition()
        self.current = None  # {"id": int, "text": str, "options": [...], "default": str}
        self.answer = None
        self._ids = itertools.count(1)

    def ask(self, text, options=("y", "n"), default="n", timeout=300):
        with self.cond:
            prompt_id = next(self._ids)
            self.current = {
                "id": prompt_id,
                "text": text,
                "options": list(options),
                "default": default,
            }
            self.answer = None
            prompt = self.current
        self.broker.publish_event("prompt", prompt)

        # 终端应答通道（与网页按钮并行，先到先生效）
        if sys.stdin is not None and sys.stdin.isatty():
            def _read_stdin(pid=prompt_id):
                try:
                    ans = input()
                    self.submit(pid, ans)
                except Exception:
                    pass
            threading.Thread(target=_read_stdin, daemon=True).start()

        deadline = time.time() + timeout
        with self.cond:
            while self.answer is None:
                remaining = deadline - time.time()
                if remaining <= 0:
                    self.answer = default
                    self.broker.publish(
                        f"\n⏱️ 等待超时，已按默认值 '{default}' 继续。\n"
                    )
                    break
                self.cond.wait(min(1.0, remaining))
            ans = self.answer
            prompt = self.current
            self.current = None
            self.answer = None
        if prompt:
            self.broker.publish_event("prompt_clear", {"id": prompt["id"]})
        self.broker.publish(f">>> {ans}\n")
        return ans

    def submit(self, prompt_id, value):
        with self.cond:
            if self.current is None or self.current["id"] != prompt_id:
                return False
            self.answer = str(value).strip().lower()
            self.cond.notify_all()
            return True

    def pending(self):
        with self.cond:
            return self.current


class _TeeStream:
    """写盘到原始终端的同时，把内容推给 ConsoleBroker。"""

    def __init__(self, stream, broker):
        self._stream = stream
        self._broker = broker

    def write(self, s):
        try:
            self._stream.write(s)
            self._stream.flush()
        except Exception:
            pass
        try:
            if isinstance(s, bytes):
                s = s.decode("utf-8", errors="replace")
            self._broker.publish(s)
        except Exception:
            pass

    def flush(self):
        try:
            self._stream.flush()
        except Exception:
            pass

    def __getattr__(self, name):
        return getattr(self._stream, name)


broker = ConsoleBroker()
prompts = PromptManager(broker)
_installed = False


def install():
    """接管 stdout/stderr。重复调用安全。"""
    global _installed
    if _installed:
        return
    sys.stdout = _TeeStream(sys.stdout, broker)
    sys.stderr = _TeeStream(sys.stderr, broker)
    _installed = True


def ask_user(text, options=("y", "n"), default="n", timeout=300):
    """替代 input()：终端与网页按钮双通道应答，超时按默认值继续。"""
    print(f"\n❓ {text}")
    print(f"   （可在终端输入，或在网页 http://127.0.0.1:8890 点击按钮；超时 {timeout}s 默认 '{default}'）")
    return prompts.ask(text, options=options, default=default, timeout=timeout)
