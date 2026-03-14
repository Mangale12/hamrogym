function renderActionButtons(id, options) {
  const editUrl = (options.edit || '#').replace('{id}', id);
  const deleteUrl = (options.delete || '#').replace('{id}', id);
  const detailUrl = (options.detail || '#').replace('{id}', id);
  const modalId = options.modal_id || '';
  const title = options.title || 'Edit';

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
  return `<div class="btn-group" role="group">${html}</div>`;
}
