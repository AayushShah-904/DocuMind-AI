"use client";

import { useCallback, useRef, useState } from "react";
import type { SourceReference, StreamEvent } from "@/types";
import { getApiUrl } from "@/lib/api";

interface UseStreamOptions {
  onToken?: (token: string) => void;
  onDone?: (sources: SourceReference[], sessionId: string, latencyMs: number) => void;
  onError?: (message: string) => void;
}

export function useStream(options: UseStreamOptions = {}) {
  const [isStreaming, setIsStreaming] = useState(false);
  const abortRef = useRef<AbortController | null>(null);

  const stream = useCallback(
    async (question: string, sessionId?: string, documentIds?: string[]) => {
      abortRef.current?.abort();
      const controller = new AbortController();
      abortRef.current = controller;

      setIsStreaming(true);

      try {
        const token = localStorage.getItem("access_token");
        const res = await fetch(`${getApiUrl()}/conversations/ask`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({
            question,
            session_id: sessionId,
            document_ids: documentIds,
          }),
          signal: controller.signal,
        });

        if (!res.ok) {
          options.onError?.("Request failed. Please try again.");
          return;
        }

        const reader = res.body?.getReader();
        if (!reader) return;

        const decoder = new TextDecoder();
        let buffer = "";

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split("\n");
          buffer = lines.pop() || "";

          for (const line of lines) {
            if (!line.startsWith("data: ")) continue;
            try {
              const event: StreamEvent = JSON.parse(line.slice(6));
              if (event.type === "token" && event.content) {
                options.onToken?.(event.content);
              } else if (event.type === "done") {
                options.onDone?.(
                  event.sources || [],
                  event.session_id || "",
                  event.latency_ms || 0
                );
              } else if (event.type === "error") {
                options.onError?.(event.content || "Unknown error");
              }
            } catch {
              // non-JSON line, skip
            }
          }
        }
      } catch (err: any) {
        if (err.name !== "AbortError") {
          options.onError?.(err.message || "Stream failed");
        }
      } finally {
        setIsStreaming(false);
      }
    },
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [options.onToken, options.onDone, options.onError]
  );

  const abort = useCallback(() => {
    abortRef.current?.abort();
    setIsStreaming(false);
  }, []);

  return { stream, abort, isStreaming };
}
