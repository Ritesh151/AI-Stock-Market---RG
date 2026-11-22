"use client";

import React, { useState } from "react";
import {
  Plus,
  Search,
  MessageSquare,
  Edit2,
  Trash2,
  Check,
  X,
  HardDrive,
} from "lucide-react";
import { Button } from "@/components/ui/Button";
import { ConversationSummary } from "@/types/rgAi";

interface ConversationSidebarProps {
  conversations: ConversationSummary[];
  activeId: string | null;
  onSelectConversation: (id: string) => void;
  onNewChat: () => void;
  onRenameConversation: (id: string, newTitle: string) => void;
  onDeleteConversation: (id: string) => void;
  onCloseMobile?: () => void;
}

export function ConversationSidebar({
  conversations,
  activeId,
  onSelectConversation,
  onNewChat,
  onRenameConversation,
  onDeleteConversation,
  onCloseMobile,
}: ConversationSidebarProps) {
  const [searchQuery, setSearchQuery] = useState("");
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editingTitle, setEditingTitle] = useState("");
  const [confirmDeleteId, setConfirmDeleteId] = useState<string | null>(null);

  const filtered = conversations.filter(
    (c) =>
      c.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (c.lastMessagePreview &&
        c.lastMessagePreview.toLowerCase().includes(searchQuery.toLowerCase()))
  );

  const handleStartRename = (conv: ConversationSummary, e: React.MouseEvent) => {
    e.stopPropagation();
    setEditingId(conv.id);
    setEditingTitle(conv.title);
  };

  const handleSaveRename = (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (editingTitle.trim()) {
      onRenameConversation(id, editingTitle.trim());
    }
    setEditingId(null);
  };

  const handleCancelRename = (e: React.MouseEvent) => {
    e.stopPropagation();
    setEditingId(null);
  };

  const handleConfirmDelete = (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    onDeleteConversation(id);
    setConfirmDeleteId(null);
  };

  return (
    <div className="flex h-full w-full flex-col bg-[#F8F8F5] border-r border-[#E8EAE4] p-3 text-xs">
      {/* New Chat Button */}
      <div className="mb-3">
        <Button
          size="sm"
          variant="primary"
          onClick={() => {
            onNewChat();
            if (onCloseMobile) onCloseMobile();
          }}
          className="w-full justify-center text-xs h-9 font-medium"
        >
          <Plus className="h-4 w-4 mr-1.5" />
          <span>New Analysis</span>
        </Button>
      </div>

      {/* Search Input */}
      <div className="relative mb-3">
        <Search className="absolute left-2.5 top-2.5 h-3.5 w-3.5 text-[#777D76]" />
        <input
          type="text"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          placeholder="Search research history..."
          className="w-full rounded-xl border border-[#E8EAE4] bg-[#FFFFFF] pl-8 pr-3 py-1.5 text-xs text-[#20251F] placeholder-[#777D76] focus:border-[#176B45] focus:outline-none transition-all"
        />
      </div>

      {/* Conversations List */}
      <div className="flex-1 overflow-y-auto space-y-1 pr-1">
        <span className="text-[10px] font-semibold uppercase tracking-wider text-[#777D76] px-2 block mb-1">
          Recent Conversations
        </span>

        {filtered.length === 0 ? (
          <div className="py-8 text-center text-xs text-[#777D76]">
            {searchQuery ? "No matching conversations." : "No saved chats yet."}
          </div>
        ) : (
          filtered.map((conv) => {
            const isActive = conv.id === activeId;
            const isEditing = editingId === conv.id;
            const isDeleting = confirmDeleteId === conv.id;

            return (
              <div
                key={conv.id}
                onClick={() => {
                  if (!isEditing && !isDeleting) {
                    onSelectConversation(conv.id);
                    if (onCloseMobile) onCloseMobile();
                  }
                }}
                className={`group relative flex items-center justify-between rounded-xl px-2.5 py-2 transition-colors cursor-pointer ${
                  isActive
                    ? "bg-[#FFFFFF] text-[#176B45] font-medium shadow-xs border border-[#176B45]/20"
                    : "text-[#20251F] hover:bg-[#F1F2ED]"
                }`}
              >
                {/* Left icon and title */}
                <div className="flex items-center gap-2 min-w-0 flex-1">
                  <MessageSquare
                    className={`h-3.5 w-3.5 shrink-0 ${
                      isActive ? "text-[#176B45]" : "text-[#777D76]"
                    }`}
                  />

                  {isEditing ? (
                    <input
                      type="text"
                      value={editingTitle}
                      onChange={(e) => setEditingTitle(e.target.value)}
                      onClick={(e) => e.stopPropagation()}
                      className="w-full rounded bg-white px-1.5 py-0.5 border border-[#176B45] text-xs text-[#20251F] focus:outline-none"
                      autoFocus
                    />
                  ) : (
                    <div className="min-w-0 flex-1">
                      <div className="truncate text-xs font-medium">
                        {conv.title}
                      </div>
                      {conv.lastMessagePreview && (
                        <div className="text-[10px] text-[#777D76] truncate">
                          {conv.lastMessagePreview}
                        </div>
                      )}
                    </div>
                  )}
                </div>

                {/* Inline Actions */}
                <div className="flex items-center gap-1 ml-2">
                  {isEditing ? (
                    <>
                      <button
                        onClick={(e) => handleSaveRename(conv.id, e)}
                        className="rounded p-1 text-[#16834A] hover:bg-green-100"
                        title="Save title"
                      >
                        <Check className="h-3 w-3" />
                      </button>
                      <button
                        onClick={handleCancelRename}
                        className="rounded p-1 text-[#777D76] hover:bg-gray-200"
                        title="Cancel rename"
                      >
                        <X className="h-3 w-3" />
                      </button>
                    </>
                  ) : isDeleting ? (
                    <div
                      className="flex items-center gap-1 bg-red-50 p-1 rounded border border-red-200"
                      onClick={(e) => e.stopPropagation()}
                    >
                      <span className="text-[10px] text-[#D64A4A] font-semibold">Delete?</span>
                      <button
                        onClick={(e) => handleConfirmDelete(conv.id, e)}
                        className="rounded px-1.5 py-0.5 bg-[#D64A4A] text-white text-[10px] font-medium"
                      >
                        Yes
                      </button>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          setConfirmDeleteId(null);
                        }}
                        className="rounded px-1 py-0.5 text-[#777D76] text-[10px]"
                      >
                        No
                      </button>
                    </div>
                  ) : (
                    <div className="opacity-0 group-hover:opacity-100 transition-opacity flex items-center gap-0.5">
                      <button
                        onClick={(e) => handleStartRename(conv, e)}
                        className="rounded p-1 text-[#777D76] hover:text-[#20251F] hover:bg-[#E8EAE4]"
                        title="Rename"
                      >
                        <Edit2 className="h-3 w-3" />
                      </button>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          setConfirmDeleteId(conv.id);
                        }}
                        className="rounded p-1 text-[#777D76] hover:text-[#D64A4A] hover:bg-red-50"
                        title="Delete"
                      >
                        <Trash2 className="h-3 w-3" />
                      </button>
                    </div>
                  )}
                </div>
              </div>
            );
          })
        )}
      </div>

      {/* Storage Transparency Notice */}
      <div className="mt-auto border-t border-[#E8EAE4] pt-2.5 px-1 text-[10px] text-[#777D76] flex items-center justify-between">
        <span className="flex items-center gap-1.5">
          <HardDrive className="h-3 w-3 text-[#176B45]" />
          <span>Local Session Storage</span>
        </span>
        <span>{conversations.length} saved</span>
      </div>
    </div>
  );
}
