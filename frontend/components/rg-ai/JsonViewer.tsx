"use client";

import React, { useState } from "react";
import { Copy, Check, Download, ChevronRight, ChevronDown, CheckCircle2 } from "lucide-react";
import { Badge } from "@/components/ui/Badge";

interface JsonViewerProps {
  data: unknown;
  schemaVersion?: string;
  requestId?: string;
}

// Recursive JSON node component for interactive expand/collapse
function JsonNode({
  keyName,
  value,
  isLast = true,
  depth = 0,
}: {
  keyName?: string;
  value: unknown;
  isLast?: boolean;
  depth?: number;
}) {
  const [isExpanded, setIsExpanded] = useState<boolean>(depth < 2);

  if (value === null) {
    return (
      <div className="font-mono text-xs leading-relaxed" style={{ paddingLeft: `${depth * 16}px` }}>
        {keyName && <span className="text-[#176B45]">{`"${keyName}"`}</span>}
        {keyName && <span className="text-[#777D76]">: </span>}
        <span className="text-[#777D76] italic font-semibold">null</span>
        {!isLast && <span className="text-[#777D76]">,</span>}
      </div>
    );
  }

  if (typeof value === "boolean") {
    return (
      <div className="font-mono text-xs leading-relaxed" style={{ paddingLeft: `${depth * 16}px` }}>
        {keyName && <span className="text-[#176B45]">{`"${keyName}"`}</span>}
        {keyName && <span className="text-[#777D76]">: </span>}
        <span className="text-blue-600 font-semibold">{value ? "true" : "false"}</span>
        {!isLast && <span className="text-[#777D76]">,</span>}
      </div>
    );
  }

  if (typeof value === "number") {
    return (
      <div className="font-mono text-xs leading-relaxed" style={{ paddingLeft: `${depth * 16}px` }}>
        {keyName && <span className="text-[#176B45]">{`"${keyName}"`}</span>}
        {keyName && <span className="text-[#777D76]">: </span>}
        <span className="text-[#16834A] font-semibold">{value}</span>
        {!isLast && <span className="text-[#777D76]">,</span>}
      </div>
    );
  }

  if (typeof value === "string") {
    return (
      <div className="font-mono text-xs leading-relaxed" style={{ paddingLeft: `${depth * 16}px` }}>
        {keyName && <span className="text-[#176B45]">{`"${keyName}"`}</span>}
        {keyName && <span className="text-[#777D76]">: </span>}
        <span className="text-[#20251F]">{`"${value}"`}</span>
        {!isLast && <span className="text-[#777D76]">,</span>}
      </div>
    );
  }

  if (Array.isArray(value)) {
    if (value.length === 0) {
      return (
        <div className="font-mono text-xs leading-relaxed" style={{ paddingLeft: `${depth * 16}px` }}>
          {keyName && <span className="text-[#176B45]">{`"${keyName}"`}</span>}
          {keyName && <span className="text-[#777D76]">: </span>}
          <span className="text-[#777D76]">[]</span>
          {!isLast && <span className="text-[#777D76]">,</span>}
        </div>
      );
    }

    return (
      <div className="font-mono text-xs leading-relaxed">
        <div
          onClick={() => setIsExpanded(!isExpanded)}
          className="flex items-center gap-1 cursor-pointer hover:bg-[#E8EAE4]/40 rounded px-1 -mx-1"
          style={{ paddingLeft: `${depth * 16}px` }}
        >
          {isExpanded ? (
            <ChevronDown className="h-3 w-3 text-[#777D76]" />
          ) : (
            <ChevronRight className="h-3 w-3 text-[#777D76]" />
          )}
          {keyName && <span className="text-[#176B45]">{`"${keyName}"`}</span>}
          {keyName && <span className="text-[#777D76]">: </span>}
          <span className="text-[#777D76]">[{!isExpanded ? `... ${value.length} items` : ""}</span>
          {!isExpanded && <span className="text-[#777D76]">]</span>}
          {!isExpanded && !isLast && <span className="text-[#777D76]">,</span>}
        </div>

        {isExpanded && (
          <div>
            {value.map((item, idx) => (
              <JsonNode
                key={idx}
                value={item}
                isLast={idx === value.length - 1}
                depth={depth + 1}
              />
            ))}
            <div style={{ paddingLeft: `${depth * 16}px` }}>
              <span className="text-[#777D76]">]</span>
              {!isLast && <span className="text-[#777D76]">,</span>}
            </div>
          </div>
        )}
      </div>
    );
  }

  if (typeof value === "object") {
    const entries = Object.entries(value as Record<string, unknown>);
    if (entries.length === 0) {
      return (
        <div className="font-mono text-xs leading-relaxed" style={{ paddingLeft: `${depth * 16}px` }}>
          {keyName && <span className="text-[#176B45]">{`"${keyName}"`}</span>}
          {keyName && <span className="text-[#777D76]">: </span>}
          <span className="text-[#777D76]">{"{}"}</span>
          {!isLast && <span className="text-[#777D76]">,</span>}
        </div>
      );
    }

    return (
      <div className="font-mono text-xs leading-relaxed">
        <div
          onClick={() => setIsExpanded(!isExpanded)}
          className="flex items-center gap-1 cursor-pointer hover:bg-[#E8EAE4]/40 rounded px-1 -mx-1"
          style={{ paddingLeft: `${depth * 16}px` }}
        >
          {isExpanded ? (
            <ChevronDown className="h-3 w-3 text-[#777D76]" />
          ) : (
            <ChevronRight className="h-3 w-3 text-[#777D76]" />
          )}
          {keyName && <span className="text-[#176B45]">{`"${keyName}"`}</span>}
          {keyName && <span className="text-[#777D76]">: </span>}
          <span className="text-[#777D76]">{"{"}{!isExpanded ? `... ${entries.length} keys` : ""}</span>
          {!isExpanded && <span className="text-[#777D76]">{"}"}</span>}
          {!isExpanded && !isLast && <span className="text-[#777D76]">,</span>}
        </div>

        {isExpanded && (
          <div>
            {entries.map(([k, v], idx) => (
              <JsonNode
                key={k}
                keyName={k}
                value={v}
                isLast={idx === entries.length - 1}
                depth={depth + 1}
              />
            ))}
            <div style={{ paddingLeft: `${depth * 16}px` }}>
              <span className="text-[#777D76]">{"}"}</span>
              {!isLast && <span className="text-[#777D76]">,</span>}
            </div>
          </div>
        )}
      </div>
    );
  }

  return null;
}

export function JsonViewer({
  data,
  schemaVersion = "1.0",
  requestId,
}: JsonViewerProps) {
  const [copied, setCopied] = useState<boolean>(false);

  const formattedJsonString = JSON.stringify(data, null, 2);

  const handleCopy = () => {
    if (typeof navigator !== "undefined" && navigator.clipboard) {
      navigator.clipboard.writeText(formattedJsonString);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const handleDownload = () => {
    const filename = `rg-ai-analysis-${requestId || Date.now()}.json`;
    const blob = new Blob([formattedJsonString], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="rounded-xl border border-[#E8EAE4] bg-[#FFFFFF] shadow-2xs overflow-hidden">
      {/* Viewer Header */}
      <div className="flex items-center justify-between border-b border-[#E8EAE4] bg-[#F8F8F5] px-4 py-2 text-xs">
        <div className="flex items-center gap-2">
          <Badge variant="positive">
            <CheckCircle2 className="h-3 w-3 mr-1 inline" />
            Verified Schema
          </Badge>
          <span className="text-[11px] font-mono text-[#777D76]">
            v{schemaVersion}
          </span>
          {requestId && (
            <span className="hidden sm:inline text-[11px] font-mono text-[#777D76]">
              • {requestId}
            </span>
          )}
        </div>

        <div className="flex items-center gap-1.5">
          <button
            onClick={handleCopy}
            className="inline-flex items-center gap-1 rounded-md border border-[#E8EAE4] bg-[#FFFFFF] px-2.5 py-1 text-[11px] font-medium text-[#20251F] hover:bg-[#F1F2ED] transition-colors cursor-pointer"
            title="Copy JSON to clipboard"
          >
            {copied ? (
              <>
                <Check className="h-3 w-3 text-[#16834A]" />
                <span className="text-[#16834A]">Copied</span>
              </>
            ) : (
              <>
                <Copy className="h-3 w-3 text-[#777D76]" />
                <span>Copy</span>
              </>
            )}
          </button>

          <button
            onClick={handleDownload}
            className="inline-flex items-center gap-1 rounded-md border border-[#E8EAE4] bg-[#FFFFFF] px-2.5 py-1 text-[11px] font-medium text-[#20251F] hover:bg-[#F1F2ED] transition-colors cursor-pointer"
            title="Download JSON file"
          >
            <Download className="h-3 w-3 text-[#777D76]" />
            <span>Download</span>
          </button>
        </div>
      </div>

      {/* JSON Tree Content */}
      <div className="max-h-96 overflow-auto p-4 bg-[#FFFFFF]">
        <JsonNode value={data} />
      </div>
    </div>
  );
}
