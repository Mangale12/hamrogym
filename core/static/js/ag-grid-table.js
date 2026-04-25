(function () {
  function compileRenderer(rendererSource) {
    if (!rendererSource) {
      return null;
    }

    if (typeof rendererSource === "function") {
      return rendererSource;
    }

    try {
      return new Function(`return (${rendererSource});`)();
    } catch (error) {
      console.error("Failed to compile AG Grid renderer:", error);
      return null;
    }
  }

  function buildColumnDefs(config) {
    const columnDefs = [];

    if (config.showSno) {
      columnDefs.push({
        colId: "__sno__",
        headerName: "S. No.",
        sortable: false,
        filter: false,
        resizable: false,
        width: 90,
        pinned: "left",
        valueGetter: function (params) {
          const rowIndex = params && params.node && typeof params.node.rowIndex === "number"
            ? params.node.rowIndex
            : 0;
          return rowIndex + 1;
        },
      });
    }

    (config.columns || []).forEach(function (column) {
      const renderer = compileRenderer(column.render);
      const isActionsColumn = column.name === "id" && /actions/i.test(column.title || "");
      const colDef = {
        colId: column.name,
        field: column.name,
        headerName: column.title || column.name,
        sortable: column.orderable !== false,
        filter: false,
        resizable: true,
        minWidth: isActionsColumn ? 200 : 140,
        width: isActionsColumn ? 220 : undefined,
        flex: isActionsColumn ? undefined : 1,
        wrapHeaderText: true,
        autoHeaderHeight: true,
        suppressMovable: false,
      };

      if (renderer) {
        colDef.cellRenderer = function (params) {
          return renderer(
            params.value,
            "display",
            params.data || {},
            { row: params && params.node ? params.node.rowIndex : 0 }
          );
        };
      }

      columnDefs.push(colDef);
    });

    return columnDefs;
  }

  function buildFieldOrder(config) {
    const fieldOrder = [];
    if (config.showSno) {
      fieldOrder.push("__sno__");
    }
    (config.columns || []).forEach(function (column) {
      fieldOrder.push(column.name);
    });
    return fieldOrder;
  }

  function buildRequestUrl(config, request, state) {
    const url = new URL(config.ajaxUrl, window.location.origin);
    const startRow = request.startRow || 0;
    const endRow = request.endRow || (startRow + config.pageLength);
    const length = Math.max(endRow - startRow, config.pageLength || 25);
    const fieldOrder = buildFieldOrder(config);

    url.searchParams.set("draw", "1");
    url.searchParams.set("start", String(startRow));
    url.searchParams.set("length", String(length));
    url.searchParams.set("search[value]", state.currentSearch || "");
    url.searchParams.set("columns[0][data]", fieldOrder[0] || "");

    const sortModel = Array.isArray(request.sortModel) ? request.sortModel : [];
    if (sortModel.length > 0) {
      const sort = sortModel[0];
      const index = fieldOrder.indexOf(sort.colId);
      if (index >= 0) {
        url.searchParams.set("order[0][column]", String(index));
        url.searchParams.set("order[0][dir]", sort.sort || "asc");
      }
    } else if (Array.isArray(config.initialOrder) && config.initialOrder.length > 0) {
      const defaultOrder = config.initialOrder[0];
      if (Array.isArray(defaultOrder) && defaultOrder.length >= 2) {
        url.searchParams.set("order[0][column]", String(defaultOrder[0]));
        url.searchParams.set("order[0][dir]", String(defaultOrder[1] || "asc"));
      }
    }

    return url.toString();
  }

  function updateStatus(config, message) {
    const el = document.getElementById(`ag-grid-status-${config.tableId}`);
    if (el) {
      el.textContent = message;
    }
  }

  function buildWrapper(api, state, config) {
    const wrapper = {
      api: api,
      ajax: {
        reload: function () {
          api.refreshInfiniteCache();
          return wrapper;
        },
      },
      search: function (value) {
        state.currentSearch = value || "";
        const input = document.getElementById(`ag-grid-search-${config.tableId}`);
        if (input) {
          input.value = state.currentSearch;
        }
        return wrapper;
      },
      page: function (target) {
        if (target === "first") {
          state.pendingStartRow = 0;
        }
        return wrapper;
      },
      draw: function () {
        api.purgeInfiniteCache();
        window.setTimeout(function () {
          api.ensureIndexVisible(0, "top");
        }, 0);
        return wrapper;
      },
      reload: function () {
        api.refreshInfiniteCache();
        return wrapper;
      },
    };

    return wrapper;
  }

  function bindToolbar(api, state, config) {
    const searchInput = document.getElementById(`ag-grid-search-${config.tableId}`);
    const refreshButton = document.getElementById(`ag-grid-refresh-${config.tableId}`);

    if (searchInput) {
      let debounceTimer = null;
      searchInput.addEventListener("input", function () {
        const nextValue = this.value || "";
        window.clearTimeout(debounceTimer);
        debounceTimer = window.setTimeout(function () {
          state.currentSearch = nextValue;
          state.pendingStartRow = 0;
          api.purgeInfiniteCache();
          api.ensureIndexVisible(0, "top");
        }, 250);
      });
    }

    if (refreshButton) {
      refreshButton.addEventListener("click", function () {
        api.refreshInfiniteCache();
      });
    }
  }

  function bindClientToolbar(api, config) {
    const searchInput = document.getElementById(config.searchInputId);
    const refreshButton = document.getElementById(config.refreshButtonId);

    if (searchInput) {
      let debounceTimer = null;
      searchInput.addEventListener("input", function () {
        const nextValue = this.value || "";
        window.clearTimeout(debounceTimer);
        debounceTimer = window.setTimeout(function () {
          api.setGridOption("quickFilterText", nextValue);
          const visibleCount = api.getDisplayedRowCount();
          const statusEl = document.getElementById(config.statusElementId);
          if (statusEl) {
            statusEl.textContent = `${visibleCount} rows`;
          }
        }, 150);
      });
    }

    if (refreshButton) {
      refreshButton.addEventListener("click", function () {
        api.refreshCells({ force: true });
        const statusEl = document.getElementById(config.statusElementId);
        if (statusEl) {
          statusEl.textContent = `${api.getDisplayedRowCount()} rows`;
        }
      });
    }
  }

  window.initAgGridTable = function (config) {
    const gridElement = document.getElementById(config.tableId);
    if (!gridElement || !window.agGrid) {
      return null;
    }

    const state = {
      currentSearch: "",
      pendingStartRow: null,
    };

    const columnDefs = buildColumnDefs(config);

    const datasource = {
      getRows: function (params) {
        const startRow = state.pendingStartRow != null ? state.pendingStartRow : params.startRow;
        const endRow = state.pendingStartRow != null
          ? state.pendingStartRow + (config.pageLength || 25)
          : params.endRow;

        state.pendingStartRow = null;
        updateStatus(config, "Loading records...");

        fetch(buildRequestUrl(config, {
          startRow: startRow,
          endRow: endRow,
          sortModel: params.sortModel || [],
        }, state), {
          credentials: "same-origin",
          headers: {
            "X-Requested-With": "XMLHttpRequest",
          },
        })
          .then(function (response) {
            if (!response.ok) {
              throw new Error(`Request failed with status ${response.status}`);
            }
            return response.json();
          })
          .then(function (payload) {
            const rows = Array.isArray(payload.data) ? payload.data : [];
            const totalRows = Number(payload.recordsFiltered != null ? payload.recordsFiltered : payload.recordsTotal);
            const safeTotal = Number.isFinite(totalRows) ? totalRows : rows.length;
            const lastRow = startRow + rows.length >= safeTotal ? safeTotal : -1;

            params.successCallback(rows, lastRow);
            if (safeTotal > 0) {
              updateStatus(config, `${safeTotal} records available`);
            } else {
              updateStatus(config, "No records found");
            }
          })
          .catch(function (error) {
            console.error("AG Grid data load failed:", error);
            params.failCallback();
            updateStatus(config, "Failed to load records");
          });
      },
    };

    const pageLength = config.pageLength || 25;
    const gridOptions = {
      columnDefs: columnDefs,
      defaultColDef: {
        sortable: true,
        filter: false,
        resizable: true,
        minWidth: 140,
        flex: 1,
      },
      rowModelType: "infinite",
      cacheBlockSize: pageLength,
      paginationPageSize: pageLength,
      maxBlocksInCache: 2,
      rowHeight: 48,
      headerHeight: 48,
      animateRows: true,
      datasource: datasource,
      getRowId: function (params) {
        return params && params.data && params.data.id != null ? String(params.data.id) : undefined;
      },
      getRowClass: function (params) {
        return params && params.data && params.data.is_overdue ? "datatable-overdue-row" : "";
      },
      overlayNoRowsTemplate: '<span class="ag-overlay-loading-center">No records found</span>',
    };

    if (window.agGrid.themeQuartz) {
      gridOptions.theme = window.agGrid.themeQuartz;
    }

    const api = window.agGrid.createGrid(gridElement, gridOptions);
    bindToolbar(api, state, config);
    updateStatus(config, "Grid ready");

    return buildWrapper(api, state, config);
  };

  window.initAgGridClientTable = function (config) {
    const gridElement = document.getElementById(config.tableId);
    if (!gridElement || !window.agGrid) {
      return null;
    }

    const gridOptions = {
      columnDefs: (config.columnDefs || []).map(function (column) {
        return {
          field: column.field,
          headerName: column.headerName || column.field,
          sortable: column.sortable !== false,
          filter: false,
          resizable: true,
          minWidth: column.minWidth || 140,
          flex: column.flex || 1,
          wrapHeaderText: true,
          autoHeaderHeight: true,
          autoHeight: true,
        };
      }),
      rowData: config.rowData || [],
      defaultColDef: {
        sortable: true,
        resizable: true,
        filter: false,
        minWidth: 140,
        flex: 1,
      },
      animateRows: true,
      rowHeight: 46,
      headerHeight: 48,
      overlayNoRowsTemplate: `<span class="ag-overlay-loading-center">${config.emptyMessage || "No rows found"}</span>`,
    };

    if (window.agGrid.themeQuartz) {
      gridOptions.theme = window.agGrid.themeQuartz;
    }

    const api = window.agGrid.createGrid(gridElement, gridOptions);
    bindClientToolbar(api, config);

    const statusEl = document.getElementById(config.statusElementId);
    if (statusEl) {
      statusEl.textContent = `${api.getDisplayedRowCount()} rows`;
    }

    return {
      api: api,
      reload: function () {
        api.refreshCells({ force: true });
      },
    };
  };
})();
