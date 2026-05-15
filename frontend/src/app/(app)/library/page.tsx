"use client";

import { useCallback, useState } from "react";
import { useDropzone } from "react-dropzone";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  UploadCloud,
  FileText,
  Trash2,
  Loader2,
  AlertCircle,
  CheckCircle2,
} from "lucide-react";
import { api } from "@/lib/api";
import type { Document } from "@/types";
import { formatBytes, formatRelativeTime, STATUS_COLORS } from "@/lib/utils";
import { cn } from "@/lib/utils";

export default function LibraryPage() {
  const queryClient = useQueryClient();
  const [uploadError, setUploadError] = useState("");

  // Fetch documents
  const { data, isLoading } = useQuery({
    queryKey: ["documents"],
    queryFn: () => api.get("/library").then((r) => r.data),
    refetchInterval: (query) => {
      // Auto-refresh if any doc is pending or processing
      const docs = (query.state.data as any)?.documents || [];
      const isProcessing = docs.some(
        (d: Document) => d.status === "pending" || d.status === "processing"
      );
      return isProcessing ? 3000 : false;
    },
  });

  const docs: Document[] = data?.documents || [];

  // Delete mutation
  const deleteMutation = useMutation({
    mutationFn: (id: string) => api.delete(`/library/${id}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["documents"] });
    },
  });

  // Upload mutation
  const uploadMutation = useMutation({
    mutationFn: async (file: File) => {
      const formData = new FormData();
      formData.append("file", file);
      return api.post("/library/upload", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
    },
    onSuccess: () => {
      setUploadError("");
      queryClient.invalidateQueries({ queryKey: ["documents"] });
    },
    onError: (err: any) => {
      setUploadError(err.response?.data?.detail || "Upload failed");
    },
  });

  const onDrop = useCallback(
    (acceptedFiles: File[]) => {
      if (acceptedFiles.length > 0) {
        uploadMutation.mutate(acceptedFiles[0]);
      }
    },
    [uploadMutation]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      "application/pdf": [".pdf"],
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document": [
        ".docx",
      ],
      "text/plain": [".txt"],
    },
    maxSize: 10 * 1024 * 1024, // 10MB
    multiple: false,
  });

  return (
    <div className="max-w-4xl mx-auto px-6 py-10">
      <div className="mb-8">
        <h1 className="text-2xl font-semibold text-ink dark:text-ink-inverse">
          Document Library
        </h1>
        <p className="text-ink-secondary dark:text-ink-tertiary text-sm mt-1">
          Upload and manage your documents for the AI to read.
        </p>
      </div>

      {/* Upload Zone */}
      <div
        {...getRootProps()}
        className={cn(
          "border-2 border-dashed rounded-xl p-10 text-center transition-colors cursor-pointer mb-8",
          isDragActive
            ? "border-accent bg-accent/5"
            : "border-surface-border dark:border-dark-border hover:border-accent/50 dark:hover:border-accent/50 hover:bg-surface-tertiary dark:hover:bg-dark-elevated"
        )}
      >
        <input {...getInputProps()} />
        <div className="w-12 h-12 rounded-full bg-accent/10 flex items-center justify-center mx-auto mb-4">
          <UploadCloud className="w-6 h-6 text-accent" />
        </div>
        <p className="font-medium text-ink dark:text-ink-inverse mb-1">
          {uploadMutation.isPending
            ? "Uploading..."
            : "Click to upload or drag and drop"}
        </p>
        <p className="text-sm text-ink-tertiary">
          PDF, DOCX, or TXT (max. 10MB)
        </p>
      </div>

      {uploadError && (
        <div className="mb-8 p-4 bg-red-50 dark:bg-red-950/30 text-red-600 dark:text-red-400 rounded-lg text-sm flex items-center gap-2">
          <AlertCircle className="w-4 h-4" />
          {uploadError}
        </div>
      )}

      {/* Document List */}
      <div>
        <h2 className="text-sm font-medium text-ink-secondary dark:text-ink-tertiary mb-4">
          Your files ({docs.length})
        </h2>

        {isLoading ? (
          <div className="flex justify-center py-10">
            <Loader2 className="w-6 h-6 animate-spin text-ink-tertiary" />
          </div>
        ) : docs.length === 0 ? (
          <div className="text-center py-12 card border-dashed">
            <FileText className="w-8 h-8 text-ink-tertiary mx-auto mb-3" />
            <p className="text-ink-secondary dark:text-ink-tertiary text-sm">
              No documents yet. Upload one above.
            </p>
          </div>
        ) : (
          <div className="space-y-3">
            {docs.map((doc) => (
              <div
                key={doc.id}
                className="card p-4 flex items-center gap-4 group"
              >
                <div
                  className={cn(
                    "w-10 h-10 rounded-lg flex items-center justify-center shrink-0",
                    doc.status === "failed"
                      ? "bg-red-50 dark:bg-red-950/30 text-red-500"
                      : "bg-surface-tertiary dark:bg-dark-elevated text-ink-secondary"
                  )}
                >
                  <FileText className="w-5 h-5" />
                </div>

                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-0.5">
                    <h3 className="font-medium text-sm text-ink dark:text-ink-inverse truncate">
                      {doc.original_filename}
                    </h3>
                    <span className={cn("badge", STATUS_COLORS[doc.status])}>
                      {doc.status === "processing" || doc.status === "pending" ? (
                        <span className="flex items-center gap-1">
                          <Loader2 className="w-3 h-3 animate-spin" />
                          {doc.status}
                        </span>
                      ) : doc.status === "ready" ? (
                        <span className="flex items-center gap-1">
                          <CheckCircle2 className="w-3 h-3" />
                          {doc.chunk_count} chunks
                        </span>
                      ) : (
                        doc.status
                      )}
                    </span>
                  </div>
                  <div className="text-xs text-ink-tertiary flex items-center gap-2">
                    <span>{formatBytes(doc.file_size_bytes)}</span>
                    <span>•</span>
                    <span>{formatRelativeTime(doc.created_at)}</span>
                    {doc.error_message && (
                      <>
                        <span>•</span>
                        <span className="text-red-500 truncate max-w-xs">
                          {doc.error_message}
                        </span>
                      </>
                    )}
                  </div>
                </div>

                <button
                  onClick={() => deleteMutation.mutate(doc.id)}
                  disabled={deleteMutation.isPending}
                  className="p-2 text-ink-tertiary hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-950/30 rounded-lg transition-colors opacity-0 group-hover:opacity-100"
                  title="Delete"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
