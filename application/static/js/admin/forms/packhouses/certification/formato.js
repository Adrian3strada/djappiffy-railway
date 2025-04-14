document.addEventListener("DOMContentLoaded", function() {  
    let pathArray = window.location.pathname.split('/');
    let certificationEntityId = pathArray[4];

    if (!isNaN(Number(certificationEntityId))) {

        let x = document.querySelector(".form-group.field-certification_entity");

        const row = document.createElement('div');
        row.classList.add('row');

        const divE = document.createElement('div');
        divE.classList.add('col');
        const label = document.createElement('label');
        label.textContent = 'Formatos ';
        
        divE.appendChild(label);
        row.appendChild(divE);

        const colum = document.createElement('div');
        colum.classList.add('col-sm-7');

        const apiUrl = `http://uno.dev.certiffy.net:8000/rest/v1/requirement-certification?certification_entity=${certificationEntityId}`;

        if(!isNaN(certificationEntityId)){
            fetch(apiUrl) 
                .then(response => response.json())
                .then(data => {
                    data.results.forEach(item => {
                        let nameLink = item.route ? `<a href="${item.route}" target="_blank" download>${item.name}</a>` : item.name;
                        let div = document.createElement('div');
                        div.classList.add('row');
                        div.innerHTML = nameLink;

                        colum.appendChild(div);
                    });
                })
                .catch(error => console.error("Error al obtener los datos:", error));
        } else {
            console.error("No se encontró un ID válido en la URL");
        }

        row.appendChild(colum);
        x.appendChild(row);
    }
});