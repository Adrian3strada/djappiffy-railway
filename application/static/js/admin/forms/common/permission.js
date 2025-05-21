document.addEventListener('DOMContentLoaded', function () {
    const isAdmin = document.querySelector('input[name$="-is_admin"]');
    const availableGroups = document.querySelector('select[name="groups"]');
    const addBtn = document.getElementById('id_groups_add_link');
    const removeBtn = document.getElementById('id_groups_remove_link');
    let originalPermissions = [];
    let chosenGroups = null;

    setTimeout(() => {
        chosenGroups = document.getElementById('id_groups_to');

        function moveAllOptions(from, to) {
            if (!from || !to) return;
            [...from.options].forEach(option => {
                to.appendChild(option);
            });
        }

        function toggleGroupSelectors(disabled) {
            if (availableGroups) availableGroups.disabled = disabled;
            if (chosenGroups) chosenGroups.disabled = disabled;
            if (addBtn) addBtn.disabled = disabled;
            if (removeBtn) removeBtn.disabled = disabled;
        }

        function getOptionValues(selectElement) {
            return [...selectElement.options].map(opt => opt.value);
        }

        function restoreOriginalPermissions() {
            const allOptions = [...availableGroups.options, ...chosenGroups.options];
            chosenGroups.innerHTML = '';
            availableGroups.innerHTML = '';

            allOptions.forEach(option => {
                if (originalPermissions.includes(option.value)) {
                    chosenGroups.appendChild(option);
                } else {
                    availableGroups.appendChild(option);
                }
            });
        }

        if (isAdmin && availableGroups && chosenGroups) {

            if (isAdmin.checked) {
                originalPermissions = getOptionValues(chosenGroups);
                moveAllOptions(availableGroups, chosenGroups);
                toggleGroupSelectors(true);
            }

            isAdmin.addEventListener('change', function () {
                if (this.checked) {
                    originalPermissions = getOptionValues(chosenGroups);
                    moveAllOptions(availableGroups, chosenGroups);
                    toggleGroupSelectors(true);

                } else {
                    restoreOriginalPermissions();
                    toggleGroupSelectors(false);

                }
            });
        }

    }, 500); 
});
