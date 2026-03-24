(function () {
  function normalizeIndex(html, index) {
    return html.replace(/\[(\d+)\]\[/g, '[' + index + '][');
  }

  function clearRow($row) {
    $row.find('input, select, textarea').each(function () {
      const $field = $(this);
      const type = ($field.attr('type') || '').toLowerCase();
      $field.removeAttr('data-selected-value');
      if (type === 'checkbox') {
        $field.prop('checked', false);
      } else if (type === 'file') {
        $field.val('');
      } else {
        $field.val('');
      }
    });
    $row.find('[data-file-preview-for]').each(function () {
      $(this)
        .attr('href', '#')
        .text('View file')
        .addClass('d-none');
    });
  }

  function updateFilePreview($row, name, value) {
    const $link = $row.find(`[data-file-preview-for="${name}"]`);
    if (!$link.length) return;

    const fileData = value && typeof value === 'object'
      ? value
      : { name: value || '', url: '' };

    if (fileData.url) {
      $link
        .attr('href', fileData.url)
        .text(fileData.name || 'View file')
        .removeClass('d-none');
      return;
    }

    $link
      .attr('href', '#')
      .text('View file')
      .addClass('d-none');
  }

  function setFieldValue($row, name, value) {
    const $field = $row.find(`[name$="[${name}]"]`);
    if (!$field.length) return;
    const tag = ($field.prop('tagName') || '').toLowerCase();
    const type = ($field.attr('type') || '').toLowerCase();
    if (type === 'checkbox') {
      $field.prop('checked', !!value);
    } else if (tag === 'select') {
      const normalizedValue = $field.prop('multiple')
        ? (Array.isArray(value) ? value : (value ? [value] : [])).map((item) => String(item))
        : (value == null ? '' : String(value));
      if ($field.prop('multiple')) {
        $field.data('selectedValues', normalizedValue);
        $field.removeAttr('data-selected-value');
      } else {
        $field.attr('data-selected-value', normalizedValue);
        $field.removeData('selectedValues');
      }
      $field.val(normalizedValue).trigger('change');
    } else if (type === 'file') {
      // Cannot set file input value for security reasons, but we can show a link.
      updateFilePreview($row, name, value);
    } else {
      $field.val(value == null ? '' : value);
    }
  }

  function conditionLabel(rowData) {
    const field = (rowData.field || '').trim();
    const operator = (rowData.operator || '').trim();
    const value = (rowData.value || '').trim();
    return [field, operator, value].filter(Boolean).join(' ') || 'Condition';
  }

  function getConditionOptions($form) {
    const rows = [];
    $form.find('.dynamic-section[data-section="conditions"] tbody.dynamic-rows tr.dynamic-row').each(function () {
      const $row = $(this);
      const id = ($row.find('[name$="[id]"]').val() || '').trim();
      const field = ($row.find('[name$="[field]"]').val() || '').trim();
      const operator = ($row.find('[name$="[operator]"]').val() || '').trim();
      const value = ($row.find('[name$="[value]"]').val() || '').trim();
      if (!id) return;
      rows.push({
        id: id,
        text: conditionLabel({ field: field, operator: operator, value: value }),
      });
    });
    return rows;
  }

  function syncRuleConditionOptions($form) {
    const options = getConditionOptions($form);
    $form.find('.dynamic-section[data-section="rules"] select[name$="[condition_id]"]').each(function () {
      const $select = $(this);
      const currentValue = $select.val();
      $select.find('option').not(':first').remove();
      options.forEach((option) => {
        const $option = $('<option></option>')
          .attr('value', option.id)
          .text(option.text);
        if (String(currentValue) === String(option.id)) {
          $option.prop('selected', true);
        }
        $select.append($option);
      });
      $select.trigger('change');
    });
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
    if (window.initializeModalSelect2) {
      window.initializeModalSelect2($row);
    }
    if (window.initializeCalendarFields) {
      window.initializeCalendarFields($row);
    }
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
      if (window.initializeModalSelect2) {
        window.initializeModalSelect2($row);
      }
      if (window.initializeCalendarFields) {
        window.initializeCalendarFields($row);
      }
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
    if (window.initializeModalSelect2) {
      window.initializeModalSelect2($form);
    }
    syncRuleConditionOptions($form);
  };

  window.resetDynamicSections = function ($form) {
    $form.find('.dynamic-section').each(function () {
      renderSection($(this), []);
    });
    syncRuleConditionOptions($form);
  };

  $(document).on('click', '.dynamic-section .add-row', function () {
    const sectionName = $(this).data('section');
    const $section = $(`.dynamic-section[data-section="${sectionName}"]`);
    if ($section.length) {
      addRow($section);
      syncRuleConditionOptions($section.closest('form'));
    }
  });

  $(document).on('click', '.dynamic-section .remove-row', function () {
    removeRow($(this).closest('tr.dynamic-row'));
    syncRuleConditionOptions($(this).closest('form'));
  });

  $(document).on('input change', '.dynamic-section[data-section="conditions"] input, .dynamic-section[data-section="conditions"] select, .dynamic-section[data-section="conditions"] textarea', function () {
    syncRuleConditionOptions($(this).closest('form'));
  });

  $(function () {
    $('.dynamic-section').each(function () {
      initSection($(this));
    });
    $('form').each(function () {
      syncRuleConditionOptions($(this));
    });
  });
})();
