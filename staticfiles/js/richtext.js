(function () {
  const TOOLBAR_GROUPS = [
    [
      { type: 'block', value: 'P', label: 'P', title: 'Paragraph' },
      { type: 'block', value: 'H2', label: 'H2', title: 'Heading 2' },
      { type: 'block', value: 'H3', label: 'H3', title: 'Heading 3' },
      { type: 'block', value: 'BLOCKQUOTE', label: '"', title: 'Quote' },
      { type: 'block', value: 'PRE', label: '</>', title: 'Code block' },
    ],
    [
      { type: 'command', value: 'bold', label: 'B', title: 'Bold' },
      { type: 'command', value: 'italic', label: 'I', title: 'Italic' },
      { type: 'command', value: 'underline', label: 'U', title: 'Underline' },
      { type: 'command', value: 'strikeThrough', label: 'S', title: 'Strike' },
    ],
    [
      { type: 'command', value: 'insertUnorderedList', label: '•', title: 'Bullet list' },
      { type: 'command', value: 'insertOrderedList', label: '1.', title: 'Numbered list' },
      { type: 'action', value: 'link', label: 'Link', title: 'Insert link' },
      { type: 'command', value: 'unlink', label: 'Unlink', title: 'Remove link' },
      { type: 'action', value: 'hr', label: 'HR', title: 'Horizontal rule' },
    ],
    [
      { type: 'command', value: 'undo', label: '↺', title: 'Undo' },
      { type: 'command', value: 'redo', label: '↻', title: 'Redo' },
      { type: 'command', value: 'removeFormat', label: 'Tx', title: 'Clear format' },
    ],
  ];

  const ALLOWED_TAGS = new Set([
    'A', 'B', 'BLOCKQUOTE', 'BR', 'CODE', 'DIV', 'EM', 'H1', 'H2', 'H3', 'H4',
    'HR', 'I', 'LI', 'OL', 'P', 'PRE', 'S', 'SPAN', 'STRONG', 'U', 'UL',
  ]);
  const ALLOWED_ATTRS = {
    A: new Set(['href', 'target', 'rel']),
  };

  function getScopeRoot(scope) {
    if (!scope) return document;
    if (scope.jquery) return scope[0];
    return scope;
  }

  function isRichTextTextarea(element) {
    return element && element.matches && element.matches('textarea[data-richtext="true"]');
  }

  function normalizeHtml(html) {
    return String(html || '')
      .replace(/<div><br><\/div>/gi, '<p><br></p>')
      .replace(/&nbsp;/gi, ' ')
      .trim();
  }

  function sanitizeNode(node) {
    if (node.nodeType === Node.TEXT_NODE) {
      return document.createTextNode(node.textContent || '');
    }
    if (node.nodeType !== Node.ELEMENT_NODE) {
      return document.createDocumentFragment();
    }

    const tagName = node.tagName.toUpperCase();
    const safeTag = ALLOWED_TAGS.has(tagName) ? tagName : 'SPAN';
    const safeNode = document.createElement(safeTag);

    Array.from(node.attributes || []).forEach((attr) => {
      const attrName = attr.name.toLowerCase();
      const allowed = ALLOWED_ATTRS[safeTag];
      if (!allowed || !allowed.has(attrName)) {
        return;
      }
      if (safeTag === 'A' && attrName === 'href') {
        const href = String(attr.value || '').trim();
        if (!href || /^javascript:/i.test(href)) {
          return;
        }
        safeNode.setAttribute('href', href);
        safeNode.setAttribute('target', '_blank');
        safeNode.setAttribute('rel', 'noopener noreferrer');
        return;
      }
      safeNode.setAttribute(attrName, attr.value);
    });

    Array.from(node.childNodes || []).forEach((child) => {
      safeNode.appendChild(sanitizeNode(child));
    });

    return safeNode;
  }

  function sanitizeHtml(html) {
    const template = document.createElement('template');
    template.innerHTML = String(html || '');
    const fragment = document.createDocumentFragment();
    Array.from(template.content.childNodes).forEach((node) => {
      fragment.appendChild(sanitizeNode(node));
    });
    const wrapper = document.createElement('div');
    wrapper.appendChild(fragment);
    return normalizeHtml(wrapper.innerHTML);
  }

  function getEditorElements(textarea) {
    return {
      shell: textarea.nextElementSibling && textarea.nextElementSibling.matches('[data-richtext-shell="true"]')
        ? textarea.nextElementSibling
        : null,
      surface: textarea._richTextSurface || null,
      counter: textarea._richTextCounter || null,
    };
  }

  function createToolbarButton(buttonConfig) {
    const button = document.createElement('button');
    button.type = 'button';
    button.className = 'richtext-toolbar__button';
    button.dataset.richtextType = buttonConfig.type;
    button.dataset.richtextValue = buttonConfig.value;
    button.title = buttonConfig.title;
    button.setAttribute('aria-label', buttonConfig.title);
    button.textContent = buttonConfig.label;
    return button;
  }

  function createShell(textarea) {
    const shell = document.createElement('div');
    shell.className = 'richtext-shell';
    shell.dataset.richtextShell = 'true';

    const toolbar = document.createElement('div');
    toolbar.className = 'richtext-toolbar';

    TOOLBAR_GROUPS.forEach((group) => {
      const groupEl = document.createElement('div');
      groupEl.className = 'richtext-toolbar__group';
      group.forEach((buttonConfig) => {
        groupEl.appendChild(createToolbarButton(buttonConfig));
      });
      toolbar.appendChild(groupEl);
    });

    const surface = document.createElement('div');
    surface.className = 'richtext-surface';
    surface.contentEditable = 'true';
    surface.dataset.richtextSurface = 'true';
    surface.dataset.placeholder = textarea.getAttribute('placeholder') || 'Write here...';

    const meta = document.createElement('div');
    meta.className = 'richtext-meta';
    meta.innerHTML = '<span>Rich text editor</span><span data-richtext-counter="true">0 words</span>';

    shell.appendChild(toolbar);
    shell.appendChild(surface);
    shell.appendChild(meta);
    textarea.insertAdjacentElement('afterend', shell);

    textarea.classList.add('d-none');
    textarea._richTextSurface = surface;
    textarea._richTextCounter = meta.querySelector('[data-richtext-counter="true"]');

    return shell;
  }

  function countWords(text) {
    return String(text || '').trim().split(/\s+/).filter(Boolean).length;
  }

  function updateCounter(textarea) {
    const { counter, surface } = getEditorElements(textarea);
    if (!counter || !surface) return;
    counter.textContent = `${countWords(surface.textContent)} words`;
  }

  function updateToolbarState(textarea) {
    const { shell } = getEditorElements(textarea);
    if (!shell) return;
    shell.querySelectorAll('.richtext-toolbar button[data-richtext-type="command"]').forEach((button) => {
      const command = button.dataset.richtextValue;
      let active = false;
      if (['bold', 'italic', 'underline', 'strikeThrough', 'insertOrderedList', 'insertUnorderedList'].includes(command)) {
        try {
          active = document.queryCommandState(command);
        } catch (error) {
          active = false;
        }
      }
      button.classList.toggle('is-active', !!active);
    });
  }

  function syncTextareaFromSurface(textarea) {
    const { surface } = getEditorElements(textarea);
    if (!surface) return;
    textarea.value = sanitizeHtml(surface.innerHTML);
    updateCounter(textarea);
  }

  function syncSurfaceFromTextarea(textarea) {
    const { surface } = getEditorElements(textarea);
    if (!surface) return;
    const sanitized = sanitizeHtml(textarea.value || '');
    if (surface.innerHTML !== sanitized) {
      surface.innerHTML = sanitized;
    }
    updateCounter(textarea);
  }

  function refreshDisabledState(textarea) {
    const { shell, surface } = getEditorElements(textarea);
    if (!shell || !surface) return;
    const disabled = !!(textarea.disabled || textarea.readOnly);
    shell.classList.toggle('is-disabled', disabled);
    surface.contentEditable = disabled ? 'false' : 'true';
    shell.querySelectorAll('.richtext-toolbar button').forEach((button) => {
      button.disabled = disabled;
    });
  }

  function focusSurface(textarea) {
    const { surface } = getEditorElements(textarea);
    if (!surface) return;
    surface.focus();
  }

  function runEditorAction(textarea, type, value) {
    const { surface } = getEditorElements(textarea);
    if (!surface || textarea.disabled || textarea.readOnly) return;
    focusSurface(textarea);
    if (type === 'block') {
      document.execCommand('formatBlock', false, value);
    } else if (type === 'action' && value === 'link') {
      const url = window.prompt('Enter the link URL');
      if (!url) return;
      document.execCommand('createLink', false, url);
    } else if (type === 'action' && value === 'hr') {
      document.execCommand('insertHorizontalRule', false, null);
    } else {
      document.execCommand(value, false, null);
    }
    syncTextareaFromSurface(textarea);
    updateToolbarState(textarea);
  }

  function handlePaste(textarea, event) {
    event.preventDefault();
    const clipboard = event.clipboardData || window.clipboardData;
    const html = clipboard ? clipboard.getData('text/html') : '';
    const text = clipboard ? clipboard.getData('text/plain') : '';
    const content = html ? sanitizeHtml(html) : sanitizeHtml(String(text || '').replace(/\n/g, '<br>'));
    document.execCommand('insertHTML', false, content);
    syncTextareaFromSurface(textarea);
  }

  function bindEditor(textarea) {
    const shell = createShell(textarea);
    const surface = textarea._richTextSurface;

    shell.addEventListener('click', function (event) {
      const button = event.target.closest('button[data-richtext-type]');
      if (!button) return;
      event.preventDefault();
      runEditorAction(textarea, button.dataset.richtextType, button.dataset.richtextValue);
    });

    surface.addEventListener('input', function () {
      syncTextareaFromSurface(textarea);
      updateToolbarState(textarea);
    });

    surface.addEventListener('keyup', function () {
      updateToolbarState(textarea);
    });

    surface.addEventListener('mouseup', function () {
      updateToolbarState(textarea);
    });

    surface.addEventListener('paste', function (event) {
      handlePaste(textarea, event);
    });

    textarea.addEventListener('change', function () {
      syncSurfaceFromTextarea(textarea);
      refreshDisabledState(textarea);
    });

    textarea.dataset.richtextInitialized = 'true';
    syncSurfaceFromTextarea(textarea);
    refreshDisabledState(textarea);
  }

  function findTextareas(scope) {
    const root = getScopeRoot(scope);
    if (!root) return [];
    if (isRichTextTextarea(root)) return [root];
    return Array.from(root.querySelectorAll('textarea[data-richtext="true"]'));
  }

  window.initializeRichTextEditors = function (scope) {
    findTextareas(scope).forEach((textarea) => {
      if (textarea.dataset.richtextInitialized === 'true') {
        syncSurfaceFromTextarea(textarea);
        refreshDisabledState(textarea);
        return;
      }
      bindEditor(textarea);
    });
  };

  window.syncRichTextEditors = function (scope) {
    findTextareas(scope).forEach((textarea) => {
      if (textarea.dataset.richtextInitialized !== 'true') {
        bindEditor(textarea);
      } else {
        syncSurfaceFromTextarea(textarea);
        refreshDisabledState(textarea);
      }
    });
  };

  window.refreshRichTextEditors = function (scope) {
    findTextareas(scope).forEach((textarea) => {
      refreshDisabledState(textarea);
      updateToolbarState(textarea);
    });
  };

  document.addEventListener('DOMContentLoaded', function () {
    window.initializeRichTextEditors(document);
  });

  document.addEventListener('shown.bs.modal', function (event) {
    window.initializeRichTextEditors(event.target);
  });
})();
