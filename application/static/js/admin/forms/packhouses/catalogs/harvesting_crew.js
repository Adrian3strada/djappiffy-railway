document.addEventListener("DOMContentLoaded", function () {
  const API_BASE_URL = "/rest/v1";
  const harvestingCrewProviderField = $("#id_harvesting_crew_provider");
  const crewChiefField = $("#id_crew_chief");

  const objectId = harvestingCrewProviderField.data("object-id");

  if (objectId) {
    getCrewChief(objectId);
  }

  harvestingCrewProviderField.on("change", function () {
    getCrewChief();
  });

  function updateFieldOptions(field, options) {
    const currentValue = field.val();
    field.empty().append(new Option("---------", "", true, true));

    if (options && !Array.isArray(options)) {
      options = [options];
    }

    if (options && options.length) {
      options.forEach((option) => {
        const isSelected = option.id == currentValue;
        field.append(
          new Option(option.name, option.id, isSelected, isSelected)
        );
      });
    }

    field.trigger("change").select2();
  }

  function fetchOptions(url) {
    return fetch(url)
      .then((response) => {
        if (!response.ok) {
          throw new Error("Error fetching data");
        }
        return response.json();
      })
      .catch((error) => {
        console.error("Error:", error);
        return [];
      });
  }

  function getCrewChief(objectId = null) {
    let id_harvesting_crew = harvestingCrewProviderField.val();

    if (!id_harvesting_crew) {
      updateFieldOptions(crewChiefField, []);
      return;
    }

    let url = `${API_BASE_URL}/catalogs/crew_chief/?harvesting_crew_provider=${id_harvesting_crew}`;

    if (objectId) {
      url += `&object_id=${objectId}`;
    }

    fetchOptions(url).then((data) => {
      updateFieldOptions(crewChiefField, data);
    });
  }
});
