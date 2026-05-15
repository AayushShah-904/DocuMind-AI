"use client";

import { useCallback, useRef, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Send, Square, FileText, ChevronDown, ChevronUp } from "lucide-react";
import ReactMarkdown from "react-markdown";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { oneDark } from "react-syntax-highlighter/dist/esm/styles/prism";
import { useStream } from "@/hooks/useStream";
import type { Message, SourceReference } from "@/types";
import { cn, formatRelativeTime } from "@/lib/utils";

interface ChatMessage extends Partial<Message> {
  id: string;
  role: "user" | "assistant";
  content: string;
  sources?: SourceReference[];
  isStreaming?: boolean;
}

export default function ChatPage() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [sessionId, setSessionId] = useState<string | undefined>();
  const bottomRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  const scrollToBottom = () =>
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });

  const { stream, abort, isStreaming } = useStream({
    onToken: (token) => {
      setMessages((prev) => {
        const last = prev[prev.length - 1];
        if (last?.isStreaming) {
          return [
            ...prev.slice(0, -1),
            { ...last, content: last.content + token },
          ];
        }
        return prev;
      });
      scrollToBottom();
    },
    onDone: (sources, sid, latencyMs) => {
      setSessionId(sid);
      setMessages((prev) => {
        const last = prev[prev.length - 1];
        if (last?.isStreaming) {
          return [
            ...prev.slice(0, -1),
            { ...last, isStreaming: false, sources, latency_ms: latencyMs },
          ];
        }
        return prev;
      });
    },
    onError: (err) => {
      setMessages((prev) => {
        const last = prev[prev.length - 1];
        if (last?.isStreaming) {
          return [
            ...prev.slice(0, -1),
            {
              ...last,
              isStreaming: false,
              content: `Error: ${err}`,
            },
          ];
        }
        return prev;
      });
    },
  });

  const sendMessage = useCallback(async () => {
    const q = input.trim();
    if (!q || isStreaming) return;

    setInput("");

    const userMsg: ChatMessage = {
      id: crypto.randomUUID(),
      role: "user",
      content: q,
    };
    const assistantMsg: ChatMessage = {
      id: crypto.randomUUID(),
      role: "assistant",
      content: "",
      isStreaming: true,
    };

    setMessages((prev) => [...prev, userMsg, assistantMsg]);
    setTimeout(scrollToBottom, 50);

    await stream(q, sessionId);
  }, [input, isStreaming, sessionId, stream]);

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="flex flex-col h-full max-w-3xl mx-auto">
      {/* Messages area */}
      <div className="flex-1 overflow-y-auto px-6 py-6 space-y-6">
        {messages.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full text-center py-20">
            <div className="w-12 h-12 rounded-xl bg-accent/10 flex items-center justify-center mb-4">
              <span className="text-xl font-bold text-accent">D</span>
            </div>
            <h2 className="text-lg font-medium text-ink dark:text-ink-inverse mb-2">
              Ask about your documents
            </h2>
            <p className="text-ink-secondary dark:text-ink-tertiary text-sm max-w-xs">
              Upload documents in the Library, then ask questions here.
            </p>
          </div>
        )}

        <AnimatePresence initial={false}>
          {messages.map((msg) => (
            <MessageBubble key={msg.id} message={msg} />
          ))}
        </AnimatePresence>
        <div ref={bottomRef} />
      </div>

      {/* Input area */}
      <div className="border-t border-surface-border dark:border-dark-border px-6 py-4">
        <div className="flex gap-3 items-end">
          <textarea
            ref={inputRef}
            className="input-base flex-1 resize-none min-h-[44px] max-h-[160px] py-3 leading-relaxed"
            placeholder="Ask a question... (Enter to send, Shift+Enter for newline)"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            rows={1}
            style={{ height: "auto" }}
            onInput={(e) => {
              const t = e.currentTarget;
              t.style.height = "auto";
              t.style.height = t.scrollHeight + "px";
            }}
          />
          {isStreaming ? (
            <button
              onClick={abort}
              className="btn-ghost text-red-500 hover:text-red-600 hover:bg-red-50 dark:hover:bg-red-950/30 px-3 py-3"
              title="Stop generating"
            >
              <Square className="w-4 h-4" />
            </button>
          ) : (
            <button
              onClick={sendMessage}
              disabled={!input.trim()}
              className="btn-primary px-3 py-3"
              title="Send"
            >
              <Send className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

function MessageBubble({ message }: { message: ChatMessage }) {
  const [showSources, setShowSources] = useState(false);
  const isUser = message.role === "user";

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      className={cn("flex gap-3", isUser && "flex-row-reverse")}
    >
      {/* Avatar */}
      <div
        className={cn(
          "w-8 h-8 rounded-full flex items-center justify-center shrink-0 text-sm",
          isUser
            ? "bg-surface-tertiary dark:bg-dark-elevated text-ink-secondary"
            : "bg-accent/10 text-accent font-semibold"
        )}
      >
        {isUser ? "🧑" : "D"}
      </div>

      {/* Content */}
      <div className={cn("flex-1 max-w-[85%]", isUser && "flex flex-col items-end")}>
        {isUser ? (
          <div className="bg-accent/10 dark:bg-accent/20 rounded-xl px-4 py-2.5 text-sm text-ink dark:text-ink-inverse">
            {message.content}
          </div>
        ) : (
          <div className="text-sm text-ink dark:text-ink-inverse leading-relaxed">
            <ReactMarkdown
              components={{
                code({ node, className, children, ...props }: any) {
                  const match = /language-(\w+)/.exec(className || "");
                  const isBlock = !props.inline;
                  return isBlock ? (
                    <SyntaxHighlighter
                      style={oneDark}
                      language={match?.[1] || "text"}
                      PreTag="div"
                      className="rounded-lg text-xs my-2"
                    >
                      {String(children).replace(/\n$/, "")}
                    </SyntaxHighlighter>
                  ) : (
                    <code className="bg-surface-tertiary dark:bg-dark-elevated px-1 py-0.5 rounded text-xs font-mono">
                      {children}
                    </code>
                  );
                },
              }}
            >
              {message.content}
            </ReactMarkdown>
            {message.isStreaming && (
              <span className="inline-block w-0.5 h-4 bg-accent animate-blink ml-0.5 align-text-bottom" />
            )}

            {/* Sources */}
            {message.sources && message.sources.length > 0 && (
              <div className="mt-3">
                <button
                  onClick={() => setShowSources(!showSources)}
                  className="flex items-center gap-1.5 text-xs text-ink-tertiary hover:text-accent transition-colors"
                >
                  <FileText className="w-3.5 h-3.5" />
                  {message.sources.length} source
                  {message.sources.length > 1 ? "s" : ""}
                  {showSources ? (
                    <ChevronUp className="w-3 h-3" />
                  ) : (
                    <ChevronDown className="w-3 h-3" />
                  )}
                </button>

                <AnimatePresence>
                  {showSources && (
                    <motion.div
                      initial={{ opacity: 0, height: 0 }}
                      animate={{ opacity: 1, height: "auto" }}
                      exit={{ opacity: 0, height: 0 }}
                      className="mt-2 space-y-2"
                    >
                      {message.sources.map((src, i) => (
                        <div
                          key={src.chunk_id}
                          className="text-xs border border-surface-border dark:border-dark-border rounded-lg px-3 py-2"
                        >
                          <div className="flex items-center justify-between mb-1">
                            <span className="font-medium text-ink dark:text-ink-inverse truncate">
                              {src.filename}
                            </span>
                            <span className="text-ink-tertiary ml-2 shrink-0">
                              score: {src.score.toFixed(3)}
                            </span>
                          </div>
                          <p className="text-ink-secondary dark:text-ink-tertiary leading-relaxed line-clamp-3">
                            {src.excerpt}
                          </p>
                        </div>
                      ))}
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            )}

            {message.latency_ms && !message.isStreaming && (
              <p className="text-xs text-ink-tertiary mt-2">
                {(message.latency_ms / 1000).toFixed(1)}s
              </p>
            )}
          </div>
        )}
      </div>
    </motion.div>
  );
}
