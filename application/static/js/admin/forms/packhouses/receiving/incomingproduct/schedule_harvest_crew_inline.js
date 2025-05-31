document.addEventListener('DOMContentLoaded', () => {

function fetchCrews(providerId) {
  return $.ajax({
    url: `/rest/v1/catalogs/harvesting-crew/?provider=${providerId}`,
    method: "GET",
    dataType: "json",
  });
}

function updateHarvestingCrewOptions($crewSelect, crews, selectedId = null) {
  $crewSelect.empty().append(new Option("---------", ""));

  crews.forEach(crew => {
    const opt = new Option(crew.name, crew.id);
    if (selectedId && crew.id == selectedId) {
      opt.selected = true;
    }
    $crewSelect.append(opt);
  });

  $crewSelect.trigger("change");
}

function bindProviderChangeEvents(context = document) {

  $(context)
    .find("select[id$='-provider']")
    .each(async function () {
      const $providerSelect = $(this);
      const alreadyBound = $providerSelect.data("bound");

      if (alreadyBound) return; 

      $providerSelect.data("bound", true); 
      const prefix = this.id.replace(/-provider$/, "");
      const $crewSelect = $(`#${prefix}-harvesting_crew`);

      $providerSelect.on("change.filterCrew", async function () {
        const newProviderId = $(this).val();
        const $crewSelect = $(`#${this.id.replace(/-provider$/, "")}-harvesting_crew`);

        if (!newProviderId || !$crewSelect.length) {
          console.warn("⚠️ Sin proveedor o sin cuadrilla. Limpiando opciones...");
          $crewSelect.empty().append(new Option("---------", ""));
          $crewSelect.trigger("change");
          return;
        }


        try {
          const crews = await fetchCrews(newProviderId);
          updateHarvestingCrewOptions($crewSelect, crews);
        } catch (err) {
          console.error("❌ Error al obtener cuadrillas:", err);
        }
      });

      const providerId = $providerSelect.val();
      if (providerId && $crewSelect.length) {
        try {
          const crews = await fetchCrews(providerId);
          const selectedCrewId = $crewSelect.val();
          updateHarvestingCrewOptions($crewSelect, crews, selectedCrewId);
        } catch (err) {
          console.error("❌ Error inicial al filtrar cuadrillas:", err);
        }
      } else if ($crewSelect.length) {
          $crewSelect.empty().append(new Option("---------", ""));
          $crewSelect.trigger("change");
        }

    });
}

function observeAddedCrewForms() {
  const observer = new MutationObserver((mutations) => {
    let triggered = false;

    for (const mutation of mutations) {
      if (!triggered) {
        triggered = true;
        setTimeout(() => bindProviderChangeEvents(), 50); // debounce 
      }
    }
  });

  document.querySelectorAll("[id$='-scheduleharvestharvestingcrew_set-group']").forEach(group => {
    observer.observe(group, { childList: true, subtree: true });
  });
}

$(document).ready(function () {
  bindProviderChangeEvents();
  observeAddedCrewForms();
});

});
