function renderActionButtons(id, options) {
  const editUrl = (options.edit || '#').replace('{id}', id);
  const deleteUrl = (options.delete || '#').replace('{id}', id);
  const detailUrl = (options.detail || '#').replace('{id}', id);
  const modalId = options.modal_id || '';
  const title = options.title || 'Edit';
  const extraActions = Array.isArray(options.extra_actions) ? options.extra_actions : [];

  let html = '';
  if (options.edit) {
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
  if (options.delete) {
    html += `
      <button type="button" class="btn btn-sm btn-outline-danger delete-btn"
        data-id="${id}"
        data-delete-url="${deleteUrl}">
        <i class="fas fa-trash"></i>
      </button>`;
  }
  extraActions.forEach((action) => {
    const actionClass = action.class_name || 'btn-outline-secondary';
    const buttonClass = action.button_class || 'open-tab-btn';
    const iconClass = action.icon_class || 'fas fa-circle';
    const buttonTitle = action.title || '';
    const buttonLabel = action.label || '';
    const actionDetailUrl = (action.detail_url || options.detail || '#').replace('{id}', id);
    const actionModalId = action.modal_id || modalId;
    const tabKey = action.tab_key || '';
    const iconHtml = iconClass ? `<i class="${iconClass}"></i>` : '';
    const labelHtml = buttonLabel ? `<span class="${iconHtml ? 'ms-1' : ''}">${buttonLabel}</span>` : '';

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
  });
  return `<div class="btn-group" role="group">${html}</div>`;
}
