(function () {
  function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
    return null;
  }

  function showAlert(type, message) {
    const container = document.getElementById('alert-container');
    if (!container) return;
    const alert = document.createElement('div');
    alert.className = `alert alert-${type} alert-dismissible fade show`;
    alert.role = 'alert';
    alert.innerHTML = `
      ${message}
      <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    container.appendChild(alert);
    setTimeout(() => alert.remove(), 5000);
  }

  function clearFieldErrors($form) {
    $form.find('.is-invalid').removeClass('is-invalid');
    $form.find('.field-error').remove();
  }

  function showFieldErrors($form, errors) {
    if (!errors) return;
    Object.entries(errors).forEach(([name, msgs]) => {
      const messages = Array.isArray(msgs) ? msgs.join(' ') : String(msgs || '');
      if (!messages) return;
      const $field = $form.find(`[name="${name}"]`);
      if ($field.length) {
        $field.addClass('is-invalid');
        const $error = $('<div class="invalid-feedback d-block field-error"></div>').text(messages);
        $field.after($error);
      }
    });
  }

  function fillForm($form, data) {
    Object.entries(data).forEach(([key, value]) => {
      const $field = $form.find(`[name="${key}"]`);
      if (!$field.length) return;
      if ($field.is(':checkbox')) {
        $field.prop('checked', !!value);
      } else {
        $field.val(value == null ? '' : value);
      }
    });
  }

  function hydrateSelect2($form) {
    $form.find('select[data-url]').each(function () {
      const $select = $(this);
      const url = $select.data('url');
      if (!url) return;

      const value = $select.val();
      if (!value || (Array.isArray(value) && value.length === 0)) return;

      const values = Array.isArray(value) ? value : [value];
      const existing = values.filter((val) => $select.find(`option[value="${val}"]`).length);

      if (existing.length === values.length) {
        $select.trigger('change');
        return;
      }

      $.get(url, { ids: values.join(',') })
        .done(function (res) {
          const results = res && res.results ? res.results : [];
          results.forEach((item) => {
            const option = new Option(item.text, item.id, true, true);
            $select.append(option);
          });
          $select.trigger('change');
        })
        .fail(function () {
          // silently ignore select hydration failures
        });
    });
  }

  window.initCrudModal = function (config) {
    const $modal = $('#' + config.modalId);
    const $form = $('#' + config.formId);
    const modalEl = document.getElementById(config.modalId);
    const idFieldName = config.idFieldName || 'id';

    function getModalInstance() {
      if (!modalEl || !window.bootstrap) return null;
      return bootstrap.Modal.getInstance(modalEl) || new bootstrap.Modal(modalEl);
    }

    function hideModal() {
      const instance = getModalInstance();
      if (instance) {
        instance.hide();
        return;
      }
      // Fallback cleanup if Bootstrap modal instance isn't available
      $modal.removeClass('show').hide();
      $('body').removeClass('modal-open');
      $('.modal-backdrop').remove();
    }

    function resetForm() {
      $form[0].reset();
      $form.find(`[name="${idFieldName}"]`).val('');
      $form.find('[name="_active_tab"]').val('');
      if (config.afterReset) config.afterReset();
      if (window.resetDynamicSections) {
        window.resetDynamicSections($form);
      }
      clearFieldErrors($form);
    }

    $modal.on('hidden.bs.modal', function () {
      resetForm();
    });

    $(document).on('click', '.edit-btn', function () {
      const detailUrl = $(this).data('detail-url');
      const title = $(this).data('title');
      const recordId = $(this).data('id');
      if (recordId) {
        $form.find(`[name="${idFieldName}"]`).val(recordId);
      }
      if (title) $modal.find('.modal-title').text(title);

      $.get(detailUrl)
        .done(function (res) {
          if (res && res.data) {
            fillForm($form, res.data);
            hydrateSelect2($form);
            clearFieldErrors($form);
            if (res.data[idFieldName]) {
              $form.find(`[name="${idFieldName}"]`).val(res.data[idFieldName]);
            }
            if (res.data.__dynamic_sections__ && window.renderDynamicSections) {
              window.renderDynamicSections($form, res.data.__dynamic_sections__);
            }
          }
        })
        .fail(function () {
          showAlert('danger', 'Failed to load record.');
        });
    });

    $(document).on('click', '.delete-btn', function () {
      const deleteUrl = $(this).data('delete-url');
      const runDelete = function () {
        $.ajax({
          url: deleteUrl,
          method: 'POST',
          headers: { 'X-CSRFToken': getCookie('csrftoken') },
        })
          .done(function () {
            if (config.table) {
              config.table.ajax.reload(null, false);
            }
            if (window.Swal) {
              Swal.fire('Deleted', `${config.entityName} deleted successfully.`, 'success');
            } else {
              showAlert('success', `${config.entityName} deleted successfully.`);
            }
          })
          .fail(function () {
            if (window.Swal) {
              Swal.fire('Failed', `Failed to delete ${config.entityName}.`, 'error');
            } else {
              showAlert('danger', `Failed to delete ${config.entityName}.`);
            }
          });
      };

      if (window.Swal) {
        Swal.fire({
          title: 'Are you sure?',
          text: `This will delete ${config.entityName}.`,
          icon: 'warning',
          showCancelButton: true,
          confirmButtonText: 'Yes, delete',
          cancelButtonText: 'Cancel',
        }).then((result) => {
          if (result.isConfirmed) runDelete();
        });
      } else {
        if (!confirm('Are you sure you want to delete this record?')) return;
        runDelete();
      }
    });

    $(document).on('click', '.tab-save-btn', function () {
      const tabKey = $(this).data('tab') || '';
      $form.find('[name="_active_tab"]').val(tabKey);
      $form.trigger('submit');
    });

    $(document).on('click', '.save-all-btn', function () {
      $form.find('[name="_active_tab"]').val('');
    });

    $form.on('submit', function (e) {
      e.preventDefault();
      clearFieldErrors($form);
      const id = $form.find(`[name="${idFieldName}"]`).val();
      const activeTab = ($form.find('[name="_active_tab"]').val() || '').trim();
      const isUpdate = !!id;
      const url = isUpdate
        ? config.updateUrlTemplate.replace('{id}', id)
        : config.createUrl;

      const formData = new FormData($form[0]);

      $.ajax({
        url: url,
        method: 'POST',
        data: formData,
        processData: false,
        contentType: false,
        headers: { 'X-CSRFToken': getCookie('csrftoken') },
      })
        .done(function (res) {
          if (res && res.id) {
            $form.find(`[name="${idFieldName}"]`).val(res.id);
          }
          if (!activeTab) {
            hideModal();
          }
          if (config.table) {
            if (!isUpdate && config.clearSearchOnCreate !== false) {
              config.table.search('').page('first').draw('page');
            } else {
              config.table.ajax.reload(null, false);
            }
          }
          showAlert('success', `${config.entityName} saved successfully.`);

          if (activeTab) {
            const $activeBtn = $modal.find(`.tab-save-btn[data-tab="${activeTab}"]`);
            const $pane = $activeBtn.closest('.tab-pane');
            const $nextPane = $pane.nextAll('.tab-pane').first();
            if ($nextPane.length) {
              const nextId = $nextPane.attr('id');
              const $nextTab = $modal.find(`[data-bs-target="#${nextId}"]`);
              if ($nextTab.length && window.bootstrap) {
                const tabInstance = new bootstrap.Tab($nextTab[0]);
                tabInstance.show();
              } else {
                $nextTab.trigger('click');
              }
            }
          }
        })
        .fail(function (xhr) {
          let message = `Failed to save ${config.entityName}.`;
          if (xhr.responseJSON && xhr.responseJSON.errors) {
            const errors = Object.values(xhr.responseJSON.errors)
              .map(err => err.join(' '))
              .join(' ');
            if (errors) message = errors;
            showFieldErrors($form, xhr.responseJSON.errors);
          }
          if (xhr.responseJSON && xhr.responseJSON.non_field_errors) {
            showAlert('danger', xhr.responseJSON.non_field_errors.join(' '));
            return;
          }
          showAlert('danger', message);
        });
    });
  };
})();
