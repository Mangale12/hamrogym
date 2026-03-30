(function () {
  const POLICY_STATIC_OPTIONS = {
    attendance_status: [
      ['', 'Select Value'],
      ['pending', 'Pending'],
      ['present', 'Present'],
      ['absent', 'Absent'],
      ['late', 'Late'],
      ['half_day', 'Half Day'],
      ['leave', 'Leave'],
    ],
    employee_type: [
      ['', 'Select Value'],
      ['full_time', 'Full time'],
      ['part_time', 'Part time'],
      ['contract', 'Contract'],
    ],
    employment_status: [
      ['', 'Select Value'],
      ['active', 'Active'],
      ['resigned', 'Resigned'],
      ['terminated', 'Terminated'],
    ],
    weekday: [
      ['', 'Select Value'],
      ['monday', 'Monday'],
      ['tuesday', 'Tuesday'],
      ['wednesday', 'Wednesday'],
      ['thursday', 'Thursday'],
      ['friday', 'Friday'],
      ['saturday', 'Saturday'],
      ['sunday', 'Sunday'],
    ],
    boolean: [
      ['', 'Select Value'],
      ['true', 'True'],
      ['false', 'False'],
    ],
    approval_status: [
      ['', 'Select Value'],
      ['pending', 'Pending'],
      ['approved', 'Approved'],
      ['rejected', 'Rejected'],
    ],
  };

  const POLICY_SELECT_URLS = {
    employee_id: '/core/employees/select/',
    department_id: '/core/departments/select/',
    designation_id: '/core/designations/select/',
    shift_id: '/core/shifts/select/',
  };

  const POLICY_OPERATOR_OPTIONS = {
    default: [
      ['eq', 'Equals'],
      ['neq', 'Not Equals'],
      ['contains', 'Contains'],
      ['is_null', 'Is Null'],
      ['not_null', 'Is Not Null'],
    ],
    reference: [
      ['eq', 'Equals'],
      ['neq', 'Not Equals'],
      ['in', 'In'],
      ['not_in', 'Not In'],
      ['is_null', 'Is Null'],
      ['not_null', 'Is Not Null'],
    ],
    choice: [
      ['eq', 'Equals'],
      ['neq', 'Not Equals'],
      ['in', 'In'],
      ['not_in', 'Not In'],
      ['is_null', 'Is Null'],
      ['not_null', 'Is Not Null'],
    ],
    time: [
      ['eq', 'Equals'],
      ['neq', 'Not Equals'],
      ['gt', 'Greater Than'],
      ['gte', 'Greater Than or Equal'],
      ['lt', 'Less Than'],
      ['lte', 'Less Than or Equal'],
      ['is_null', 'Is Null'],
      ['not_null', 'Is Not Null'],
    ],
    boolean: [
      ['is_true', 'Is True'],
      ['is_false', 'Is False'],
      ['eq', 'Equals'],
      ['neq', 'Not Equals'],
      ['is_null', 'Is Null'],
      ['not_null', 'Is Not Null'],
    ],
  };

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
      const field = ($row.find('[name$="[field_name]"]').val() || '').trim();
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

  function createSelect(name, options, value, extraAttrs) {
    const $select = $('<select class="form-select"></select>').attr('name', name);
    (options || []).forEach((option) => {
      const optionValue = Array.isArray(option) ? option[0] : option.value;
      const optionLabel = Array.isArray(option) ? option[1] : option.label;
      const $option = $('<option></option>').attr('value', optionValue).text(optionLabel);
      if (String(value || '') === String(optionValue || '')) {
        $option.prop('selected', true);
      }
      $select.append($option);
    });
    Object.entries(extraAttrs || {}).forEach(([key, attrValue]) => {
      $select.attr(key, attrValue);
    });
    return $select;
  }

  function createInput(name, type, value) {
    return $('<input class="form-control">')
      .attr('name', name)
      .attr('type', type)
      .val(value == null ? '' : value);
  }

  function createTextarea(name, value) {
    return $('<textarea class="form-control" rows="2"></textarea>')
      .attr('name', name)
      .val(value == null ? '' : value);
  }

  function replaceDynamicField($field, $replacement) {
    $field.replaceWith($replacement);
    if (window.initializeModalSelect2) {
      window.initializeModalSelect2($replacement.closest('tr'));
    }
  }

  function policyConditionMeta(fieldName) {
    if (POLICY_SELECT_URLS[fieldName]) {
      return {
        kind: 'ajax_select',
        url: POLICY_SELECT_URLS[fieldName],
        operators: POLICY_OPERATOR_OPTIONS.reference,
      };
    }
    if (fieldName === 'employee_type') {
      return {
        kind: 'static_select',
        options: POLICY_STATIC_OPTIONS.employee_type,
        operators: POLICY_OPERATOR_OPTIONS.choice,
      };
    }
    if (fieldName === 'employment_status') {
      return {
        kind: 'static_select',
        options: POLICY_STATIC_OPTIONS.employment_status,
        operators: POLICY_OPERATOR_OPTIONS.choice,
      };
    }
    if (fieldName === 'attendance_status') {
      return {
        kind: 'static_select',
        options: POLICY_STATIC_OPTIONS.attendance_status,
        operators: POLICY_OPERATOR_OPTIONS.choice,
      };
    }
    if (fieldName === 'overtime_status') {
      return {
        kind: 'static_select',
        options: POLICY_STATIC_OPTIONS.approval_status,
        operators: POLICY_OPERATOR_OPTIONS.choice,
      };
    }
    if (fieldName === 'weekday') {
      return {
        kind: 'static_select',
        options: POLICY_STATIC_OPTIONS.weekday,
        operators: POLICY_OPERATOR_OPTIONS.choice,
      };
    }
    if (fieldName === 'overtime_date') {
      return { kind: 'date', operators: POLICY_OPERATOR_OPTIONS.time };
    }
    if (
      fieldName === 'check_in_time' ||
      fieldName === 'check_out_time' ||
      fieldName === 'overtime_start_time' ||
      fieldName === 'overtime_end_time'
    ) {
      return { kind: 'time', operators: POLICY_OPERATOR_OPTIONS.time };
    }
    if (fieldName === 'is_late' || fieldName === 'is_half_day') {
      return {
        kind: 'static_select',
        options: POLICY_STATIC_OPTIONS.boolean,
        operators: POLICY_OPERATOR_OPTIONS.boolean,
      };
    }
    if (
      fieldName === 'requested_hours' ||
      fieldName === 'overtime_hours' ||
      fieldName === 'overtime_rate' ||
      fieldName === 'overtime_amount'
    ) {
      return { kind: 'text', operators: POLICY_OPERATOR_OPTIONS.time };
    }
    return { kind: 'text', operators: POLICY_OPERATOR_OPTIONS.default };
  }

  function syncPolicyConditionOperator($row, meta) {
    const $operatorField = $row.find('select[name$="[operator]"]');
    if (!$operatorField.length) return;

    const currentValue = $operatorField.val() || '';
    const allowedOptions = meta.operators || POLICY_OPERATOR_OPTIONS.default;
    const allowedValues = allowedOptions.map((item) => String(item[0]));

    $operatorField.empty();
    allowedOptions.forEach(([value, label]) => {
      const $option = $('<option></option>').attr('value', value).text(label);
      if (String(currentValue) === String(value)) {
        $option.prop('selected', true);
      }
      $operatorField.append($option);
    });

    if (!allowedValues.includes(String(currentValue)) && allowedOptions.length) {
      $operatorField.val(allowedOptions[0][0]);
    }
  }

  function syncPolicyConditionRow($row) {
    const $fieldName = $row.find('select[name$="[field_name]"]');
    const $valueField = $row.find('[name$="[value]"]');
    if (!$fieldName.length || !$valueField.length) return;

    const currentValue = $valueField.is('select')
      ? ($valueField.attr('data-selected-value') || $valueField.val())
      : $valueField.val();
    const name = $valueField.attr('name');
    const meta = policyConditionMeta($fieldName.val());

    syncPolicyConditionOperator($row, meta);

    let $replacement;

    if (meta.kind === 'ajax_select') {
      $replacement = createSelect(name, [['', 'Select Value']], currentValue, {
        'data-url': meta.url,
        'data-selected-value': currentValue == null ? '' : currentValue,
      });
    } else if (meta.kind === 'static_select') {
      $replacement = createSelect(name, meta.options, currentValue);
    } else if (meta.kind === 'time') {
      $replacement = createInput(name, 'time', currentValue);
    } else if (meta.kind === 'date') {
      $replacement = createInput(name, 'date', currentValue);
    } else {
      $replacement = createInput(name, 'text', currentValue);
    }

    if ($valueField.prop('tagName') !== $replacement.prop('tagName') || $valueField.attr('type') !== $replacement.attr('type') || $valueField.attr('data-url') !== $replacement.attr('data-url')) {
      replaceDynamicField($valueField, $replacement);
      return;
    }

    if ($replacement.is('select')) {
      $valueField.replaceWith($replacement);
      if (window.initializeModalSelect2) {
        window.initializeModalSelect2($row);
      }
      return;
    }

    $valueField.attr('type', $replacement.attr('type') || 'text').val(currentValue == null ? '' : currentValue);
  }

  function policyActionValueMeta(actionType, targetField) {
    if (actionType === 'APPEND_REMARK') {
      return { kind: 'textarea' };
    }
    if (actionType === 'SET_STATUS') {
      return { kind: 'static_select', options: POLICY_STATIC_OPTIONS.attendance_status };
    }
    if (actionType === 'SET_FIELD') {
      if (targetField === 'status') {
        return { kind: 'static_select', options: POLICY_STATIC_OPTIONS.attendance_status };
      }
      if (targetField === 'is_late' || targetField === 'is_half_day') {
        return { kind: 'static_select', options: POLICY_STATIC_OPTIONS.boolean };
      }
      if (targetField === 'remarks') {
        return { kind: 'textarea' };
      }
      return { kind: 'text' };
    }
    return { kind: 'hidden_text' };
  }

  function syncPolicyActionRow($row) {
    const $actionType = $row.find('select[name$="[action_type]"]');
    const $targetField = $row.find('select[name$="[target_field]"]');
    const $valueField = $row.find('[name$="[action_value]"]');
    if (!$actionType.length || !$targetField.length || !$valueField.length) return;

    const actionType = $actionType.val() || '';
    const currentValue = $valueField.val();
    const name = $valueField.attr('name');
    const meta = policyActionValueMeta(actionType, $targetField.val() || '');
    let $replacement;

    if (actionType === 'MARK_LATE' || actionType === 'MARK_HALF_DAY' || actionType === 'SET_STATUS' || actionType === 'APPEND_REMARK') {
      $targetField.val('').prop('disabled', true);
    } else {
      $targetField.prop('disabled', false);
    }

    if (meta.kind === 'textarea') {
      $replacement = createTextarea(name, currentValue);
    } else if (meta.kind === 'static_select') {
      $replacement = createSelect(name, meta.options, currentValue);
    } else if (meta.kind === 'hidden_text') {
      $replacement = createInput(name, 'text', '');
      $replacement.prop('disabled', true);
      $replacement.attr('placeholder', 'Not required');
    } else {
      $replacement = createInput(name, 'text', currentValue);
    }

    replaceDynamicField($valueField, $replacement);
  }

  function syncPolicySections($scope) {
    $scope.find('.dynamic-section[data-section="conditions"] tbody.dynamic-rows tr.dynamic-row').each(function () {
      syncPolicyConditionRow($(this));
    });
    $scope.find('.dynamic-section[data-section="actions"] tbody.dynamic-rows tr.dynamic-row').each(function () {
      syncPolicyActionRow($(this));
    });
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
    if (window.initializeCalendarSwitchFields) {
      window.initializeCalendarSwitchFields($row);
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
      if (window.initializeCalendarSwitchFields) {
        window.initializeCalendarSwitchFields($row);
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
    syncPolicySections($form);
    syncRuleConditionOptions($form);
  };

  window.resetDynamicSections = function ($form) {
    $form.find('.dynamic-section').each(function () {
      renderSection($(this), []);
    });
    syncPolicySections($form);
    syncRuleConditionOptions($form);
  };

  $(document).on('click', '.dynamic-section .add-row', function () {
    const sectionName = $(this).data('section');
    const $section = $(`.dynamic-section[data-section="${sectionName}"]`);
    if ($section.length) {
      addRow($section);
      syncPolicySections($section.closest('form'));
      syncRuleConditionOptions($section.closest('form'));
    }
  });

  $(document).on('click', '.dynamic-section .remove-row', function () {
    removeRow($(this).closest('tr.dynamic-row'));
    syncRuleConditionOptions($(this).closest('form'));
  });

  $(document).on('input change', '.dynamic-section[data-section="conditions"] input, .dynamic-section[data-section="conditions"] select, .dynamic-section[data-section="conditions"] textarea', function () {
    syncPolicySections($(this).closest('form'));
    syncRuleConditionOptions($(this).closest('form'));
  });

  $(document).on('change', '.dynamic-section[data-section="actions"] select, .dynamic-section[data-section="actions"] input, .dynamic-section[data-section="actions"] textarea', function () {
    syncPolicySections($(this).closest('form'));
  });

  $(function () {
    $('.dynamic-section').each(function () {
      initSection($(this));
    });
    $('form').each(function () {
      syncPolicySections($(this));
      syncRuleConditionOptions($(this));
    });
  });
})();
