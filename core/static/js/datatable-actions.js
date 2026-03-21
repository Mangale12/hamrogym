function renderActionButtons(id, options, row) {
  const editUrl = (options.edit || '#').replace('{id}', id);
  const deleteUrl = (options.delete || '#').replace('{id}', id);
  const detailUrl = (options.detail || '#').replace('{id}', id);
  const modalId = options.modal_id || '';
  const title = options.title || 'Edit';
  const viewTitle = options.view_title || 'View';
  const extraActions = Array.isArray(options.extra_actions) ? options.extra_actions : [];
  const stateField = options.action_state_field || '';
  const stateValue = stateField && row ? row[stateField] : undefined;
  const hideEditOnValues = Array.isArray(options.hide_edit_on_values) ? options.hide_edit_on_values.map(String) : [];
  const hideDeleteOnValues = Array.isArray(options.hide_delete_on_values) ? options.hide_delete_on_values.map(String) : [];
  const normalizedStateValue = stateValue == null ? '' : String(stateValue);

  let html = '';
  if (options.view) {
    html += `
      <button type="button" class="btn btn-sm btn-outline-info view-btn"
        data-id="${id}"
        data-detail-url="${detailUrl}"
        data-bs-toggle="modal"
        data-bs-target="${modalId}"
        data-title="${viewTitle}">
        <i class="fas fa-eye"></i>
      </button>`;
  }
  if (options.edit && !hideEditOnValues.includes(normalizedStateValue)) {
    html += `
      <button type="button" class="btn btn-sm btn-outline-primary edit-btn"
        data-id="${id}"
        data-detail-url="${detailUrl}"
        data-edit-url="${editUrl}"
        data-bs-toggle="modal"
        data-bs-target="${modalId}"
        data-title="${title}">
        <i class="fas fa-edit"></i>
      </button>`;
  }
  if (options.delete && !hideDeleteOnValues.includes(normalizedStateValue)) {
    html += `
      <button type="button" class="btn btn-sm btn-outline-danger delete-btn"
        data-id="${id}"
        data-delete-url="${deleteUrl}">
        <i class="fas fa-trash"></i>
      </button>`;
  }
  extraActions.forEach((action) => {
    const hideOnValues = Array.isArray(action.hide_on_values) ? action.hide_on_values.map(String) : [];
    if (hideOnValues.includes(normalizedStateValue)) {
      return;
    }
    const actionClass = action.class_name || 'btn-outline-secondary';
    const actionUrl = action.action_url ? action.action_url.replace('{id}', id) : '';
    const buttonClass = actionUrl ? (action.button_class || 'entity-post-action-btn') : (action.button_class || 'open-tab-btn');
    const iconClass = action.icon_class || 'fas fa-circle';
    const buttonTitle = action.title || '';
    const buttonLabel = action.label || '';
    const actionDetailUrl = (action.detail_url || options.detail || '#').replace('{id}', id);
    const actionModalId = action.modal_id || modalId;
    const tabKey = action.tab_key || '';
    const iconHtml = iconClass ? `<i class="${iconClass}"></i>` : '';
    const labelHtml = buttonLabel ? `<span class="${iconHtml ? 'ms-1' : ''}">${buttonLabel}</span>` : '';
    if (actionUrl) {
      const confirmText = action.confirm_text || '';
      const successMessage = action.success_message || '';
      html += `
        <button type="button" class="btn btn-sm ${actionClass} ${buttonClass}"
          data-id="${id}"
          data-action-url="${actionUrl}"
          data-confirm-text="${confirmText}"
          data-success-message="${successMessage}"
          data-title="${buttonTitle}"
          title="${buttonTitle}">
          ${iconHtml}${labelHtml}
        </button>`;
    } else {
      html += `
        <button type="button" class="btn btn-sm ${actionClass} ${buttonClass}"
          data-id="${id}"
          data-detail-url="${actionDetailUrl}"
          data-bs-toggle="modal"
          data-bs-target="${actionModalId}"
          data-tab-key="${tabKey}"
          data-title="${buttonTitle}"
          title="${buttonTitle}">
          ${iconHtml}${labelHtml}
        </button>`;
    }
  });
  return `<div class="datatable-action-group" role="group">${html}</div>`;
}
