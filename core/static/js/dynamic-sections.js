(function () {
  function normalizeIndex(html, index) {
    return html.replace(/\[(\d+)\]\[/g, '[' + index + '][');
  }

  function clearRow($row) {
    $row.find('input, select, textarea').each(function () {
      const $field = $(this);
      const type = ($field.attr('type') || '').toLowerCase();
      if (type === 'checkbox') {
        $field.prop('checked', false);
      } else if (type === 'file') {
        $field.val('');
      } else {
        $field.val('');
      }
    });
  }

  function setFieldValue($row, name, value) {
    const $field = $row.find(`[name$="[${name}]"]`);
    if (!$field.length) return;
    const tag = ($field.prop('tagName') || '').toLowerCase();
    const type = ($field.attr('type') || '').toLowerCase();
    if (type === 'checkbox') {
      $field.prop('checked', !!value);
    } else if (tag === 'select') {
      $field.val(value == null ? '' : value).trigger('change');
    } else if (type === 'file') {
      // Cannot set file input value for security reasons.
    } else {
      $field.val(value == null ? '' : value);
    }
  }

  function initSection($section) {
    const $tbody = $section.find('tbody.dynamic-rows');
    if (!$tbody.length) return;
    if (!$section.data('template')) {
      const $templateRow = $tbody.find('tr.dynamic-row').first();
      if ($templateRow.length) {
        $section.data('template', $templateRow.prop('outerHTML'));
      }
    }
  }

  function addRow($section) {
    initSection($section);
    const template = $section.data('template');
    if (!template) return;
    const $tbody = $section.find('tbody.dynamic-rows');
    const index = $tbody.find('tr.dynamic-row').length;
    const html = normalizeIndex(template, index);
    const $row = $(html);
    clearRow($row);
    $tbody.append($row);
  }

  function removeRow($row) {
    const $tbody = $row.closest('tbody.dynamic-rows');
    if ($tbody.find('tr.dynamic-row').length <= 1) {
      clearRow($row);
      return;
    }
    $row.remove();
  }

  function renderSection($section, rows) {
    initSection($section);
    const template = $section.data('template');
    if (!template) return;
    const $tbody = $section.find('tbody.dynamic-rows');
    $tbody.empty();

    const safeRows = Array.isArray(rows) && rows.length ? rows : [{}];
    safeRows.forEach((rowData, index) => {
      const html = normalizeIndex(template, index);
      const $row = $(html);
      Object.entries(rowData || {}).forEach(([key, value]) => {
        setFieldValue($row, key, value);
      });
      $tbody.append($row);
    });
  }

  window.renderDynamicSections = function ($form, sectionsData) {
    if (!sectionsData) return;
    Object.entries(sectionsData).forEach(([sectionName, rows]) => {
      const $section = $form.find(`.dynamic-section[data-section="${sectionName}"]`);
      if ($section.length) {
        renderSection($section, rows);
      }
    });
  };

  window.resetDynamicSections = function ($form) {
    $form.find('.dynamic-section').each(function () {
      renderSection($(this), []);
    });
  };

  $(document).on('click', '.dynamic-section .add-row', function () {
    const sectionName = $(this).data('section');
    const $section = $(`.dynamic-section[data-section="${sectionName}"]`);
    if ($section.length) {
      addRow($section);
    }
  });

  $(document).on('click', '.dynamic-section .remove-row', function () {
    removeRow($(this).closest('tr.dynamic-row'));
  });

  $(function () {
    $('.dynamic-section').each(function () {
      initSection($(this));
    });
  });
})();
