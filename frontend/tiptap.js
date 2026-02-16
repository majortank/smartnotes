import { Editor } from "@tiptap/core";
import StarterKit from "@tiptap/starter-kit";
import Link from "@tiptap/extension-link";
import Placeholder from "@tiptap/extension-placeholder";
import Underline from "@tiptap/extension-underline";
import MarkdownIt from "markdown-it";
import "./tiptap.css";

const editorElement = document.getElementById("tiptap-editor");
const inputElement = document.getElementById("tiptap-input");
const toolbarElement = document.getElementById("tiptap-toolbar");

if (editorElement && inputElement) {
  const markdownParser = new MarkdownIt({
    html: false,
    linkify: true,
    breaks: true,
  });

  const editor = new Editor({
    element: editorElement,
    extensions: [
      StarterKit,
      Underline,
      Link.configure({
        openOnClick: false,
        autolink: true,
        defaultProtocol: "https",
      }),
      Placeholder.configure({
        placeholder: "Write your thoughts here...",
      }),
    ],
    content: inputElement.value || "",
    onUpdate: ({ editor }) => {
      inputElement.value = editor.getHTML();
      toggleActiveStates(editor);
    },
    onSelectionUpdate: ({ editor }) => {
      toggleActiveStates(editor);
    },
  });

  editor.view.dom.addEventListener("paste", (event) => {
    const clipboard = event.clipboardData;
    if (!clipboard) {
      return;
    }
    const html = clipboard.getData("text/html");
    const text = clipboard.getData("text/plain");
    if (!text) {
      return;
    }
    const htmlLooksPlain = html && isHtmlPlainText(html, text);
    if (!isLikelyMarkdown(text)) {
      return;
    }
    if (html && html.trim() && !htmlLooksPlain) {
      return;
    }
    event.preventDefault();
    const rendered = markdownParser.render(text);
    editor.commands.insertContent(rendered);
  });

  toggleActiveStates(editor);

  const form = inputElement.closest("form");
  if (form) {
    form.addEventListener("submit", () => {
      inputElement.value = editor.getHTML();
    });
  }

  if (toolbarElement) {
    toolbarElement.addEventListener("click", (event) => {
      const button = event.target.closest("button[data-action]");
      if (!button) {
        return;
      }
      event.preventDefault();
      const action = button.dataset.action;

      switch (action) {
        case "bold":
          editor.chain().focus().toggleBold().run();
          break;
        case "italic":
          editor.chain().focus().toggleItalic().run();
          break;
        case "underline":
          editor.chain().focus().toggleUnderline().run();
          break;
        case "strike":
          editor.chain().focus().toggleStrike().run();
          break;
        case "bulletList":
          editor.chain().focus().toggleBulletList().run();
          break;
        case "orderedList":
          editor.chain().focus().toggleOrderedList().run();
          break;
        case "blockquote":
          editor.chain().focus().toggleBlockquote().run();
          break;
        case "codeBlock":
          editor.chain().focus().toggleCodeBlock().run();
          break;
        case "heading2":
          editor.chain().focus().toggleHeading({ level: 2 }).run();
          break;
        case "heading3":
          editor.chain().focus().toggleHeading({ level: 3 }).run();
          break;
        case "link":
          setLink(editor);
          break;
        default:
          break;
      }
      toggleActiveStates(editor);
    });
  }
}

function isLikelyMarkdown(text) {
  const markdownSignals = [
    /^#{1,6}\s/m,
    /^\s*[-*+]\s+/m,
    /^\s*\d+\.\s+/m,
    /\*\*[^\n]+\*\*/,
    /`{3}[\s\S]*`{3}/,
    /`[^`]+`/,
    /\[[^\]]+\]\([^)]+\)/,
    />\s+.+/m,
  ];
  return markdownSignals.some((pattern) => pattern.test(text));
}

function isHtmlPlainText(html, text) {
  const stripped = html.replace(/<[^>]*>/g, "").replace(/\s+/g, " ").trim();
  const normalizedText = text.replace(/\s+/g, " ").trim();
  return stripped === normalizedText;
}

function setLink(editor) {
  const previousUrl = editor.getAttributes("link").href;
  const url = window.prompt("Enter link URL", previousUrl || "");
  if (url === null) {
    return;
  }
  if (url === "") {
    editor.chain().focus().extendMarkRange("link").unsetLink().run();
    return;
  }
  editor.chain().focus().extendMarkRange("link").setLink({ href: url }).run();
}

function toggleActiveStates(editor) {
  const buttons = document.querySelectorAll("#tiptap-toolbar [data-action]");
  buttons.forEach((button) => {
    const action = button.dataset.action;
    let active = false;

    switch (action) {
      case "bold":
        active = editor.isActive("bold");
        break;
      case "italic":
        active = editor.isActive("italic");
        break;
      case "underline":
        active = editor.isActive("underline");
        break;
      case "strike":
        active = editor.isActive("strike");
        break;
      case "bulletList":
        active = editor.isActive("bulletList");
        break;
      case "orderedList":
        active = editor.isActive("orderedList");
        break;
      case "blockquote":
        active = editor.isActive("blockquote");
        break;
      case "codeBlock":
        active = editor.isActive("codeBlock");
        break;
      case "heading2":
        active = editor.isActive("heading", { level: 2 });
        break;
      case "heading3":
        active = editor.isActive("heading", { level: 3 });
        break;
      case "link":
        active = editor.isActive("link");
        break;
      default:
        active = false;
        break;
    }

    button.classList.toggle("is-active", active);
  });
}
