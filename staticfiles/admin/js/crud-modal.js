function initCrudModal(options) {
    const {
        modalId,
        formId,
        table,
        createUrl,
        updateUrlTemplate,
        detailUrlTemplate,
        deleteUrlTemplate,
        idFieldName = 'id', // input name for ID
        entityName = 'Item',
        afterReset = () => {}
    } = options;

    const $modal = $(`#${modalId}`);
    const $form = $(`#${formId}`);

    // === SUBMIT FORM ===
    $form.on('submit', function(e) {
        e.preventDefault();
        const formData = new FormData(this);
        const id = formData.get(idFieldName);
        const url = id ? updateUrlTemplate.replace('{id}', id) : createUrl;

        $.ajax({
            url: url,
            method: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            headers: { 'X-CSRFTOKEN': $('input[name=csrfmiddlewaretoken]').val() },
            success: function() {
                // Hide modal + fix backdrop
                $modal.modal('hide');
                $('.modal-backdrop').remove();
                $('body').removeClass('modal-open');
                $('body').css('padding-right', '');

                table.ajax.reload();
                showAlert(`${entityName} saved successfully`);
            },
            error: function (xhr) {
                clearFormErrors($form);
            
                if (xhr.responseJSON && xhr.responseJSON.errors) {
                    const errors = xhr.responseJSON.errors;
            
                    Object.keys(errors).forEach(field => {
                        const messages = errors[field];
            
                        // Non-field errors
                        if (field === '__all__') {
                            showAlert(messages.join('<br>'), 'danger');
                            return;
                        }
            
                        const $input = $form.find(`[name="${field}"]`);
                        if ($input.length) {
                            $input.addClass('is-invalid');
            
                            const feedback = `
                                <div class="invalid-feedback">
                                    ${messages.join('<br>')}
                                </div>
                            `;
            
                            if ($input.next('.invalid-feedback').length === 0) {
                                $input.after(feedback);
                            }
                        }
                    });
                } else {
                    showAlert(`Failed to save ${entityName}`, 'danger');
                }
            }
        });
    });

    // === RESET ON CLOSE ===
    $modal.on('hidden.bs.modal', function() {
        $form[0].reset();
        clearFormErrors($form);
        $form.find(`input[name="${idFieldName}"]`).val('');
        afterReset();
    });

    // === EDIT BUTTON ===
    $(document).on('click', `.edit-${modalId.replace('Modal', '').toLowerCase()}`, function() {
        const id = $(this).data('id');
        $.get(detailUrlTemplate.replace('{id}', id))
            .done(data => {
                // Fill all fields that exist in form
                Object.keys(data).forEach(key => {
                    const $field = $form.find(`[name="${key}"]`);
                    if ($field.length) {
                        if ($field.is(':checkbox')) {
                            $field.prop('checked', !!data[key]);
                        } else {
                            $field.val(data[key] || '');
                        }
                    }
                });
                // Update title
                $modal.find('.modal-title').text(`Edit ${entityName}`);
                $modal.modal('show');
            })
            .fail(() => showAlert('Failed to load record', 'danger'));
    });

    // === DELETE BUTTON ===
    $(document).on('click', `.delete-${modalId.replace('Modal', '').toLowerCase()}`, function() {
        if (!confirm(`Delete this ${entityName.toLowerCase()}?`)) return;
        const id = $(this).data('id');
        $.ajax({
            url: deleteUrlTemplate.replace('{id}', id),
            method: 'POST',
            headers: { 'X-CSRFTOKEN': $('input[name=csrfmiddlewaretoken]').val() },
            success: () => {
                table.ajax.reload();
                showAlert(`${entityName} deleted successfully`);
            },
            error: () => showAlert('Delete failed', 'danger')
        });
    });
}

function showAlert(message, type = 'success') {
    const alert = `
        <div class="alert alert-${type} alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>`;
    $('#alert-container').html(alert);
    setTimeout(() => $('#alert-container .alert').alert('close'), 5000);
}

function clearFormErrors($form) {
    $form.find('.is-invalid').removeClass('is-invalid');
    $form.find('.invalid-feedback').remove();
}
