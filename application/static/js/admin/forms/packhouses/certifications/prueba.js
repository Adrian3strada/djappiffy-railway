document.addEventListener("DOMContentLoaded", function() {  
    console.log("LLego");
    // const tabla = document.createElement('table');

    // let table1 = document.getElementById("general-tab");
    // table1 = table1.querySelector(".card");

    // // Crear el encabezado
    // const thead = document.createElement('thead');
    // thead.innerHTML = `
    // <tr>
    //     <th>Formatos</th>
    // </tr>
    // `;
    // tabla.appendChild(thead);

    // // Crear el cuerpo
    // const tbody = document.createElement('tbody');
    // let pathArray = window.location.pathname.split('/');
    // let certificationEntityId = pathArray[4];

    // const apiUrl = `http://uno.dev.certiffy.net:8000/rest/v1/requirement-certification?certification_entity=${certificationEntityId}`;

    // if(!isNaN(certificationEntityId)){
    //     fetch(apiUrl)  // Cambia la URL a la de tu API
    //         .then(response => response.json())
    //         .then(data => {
    //             data.results.forEach(item => {
    //                 let nameLink = item.route ? `<a href="${item.route}" target="_blank" download>${item.name}</a>` : item.name;
    //                 let row = `<tr>
    //                     <td>${nameLink}</td>
    //                 </tr>`;
    //                 tbody.innerHTML += row;
    //             });
    //         })
    //         .catch(error => console.error("Error al obtener los datos:", error));
    // } else {
    //     console.error("No se encontró un ID válido en la URL");
    // }

    // tabla.appendChild(tbody);

    // table1.appendChild(tabla);

    // -----------------------------------------------

    let x = document.querySelector(".form-group.field-certification_entity");
    console.log(x);

    const row = document.createElement('div');
    row.classList.add('row');

    const label = document.createElement('label');
    label.textContent = 'Formatos';
    row.appendChild(label);

    const colum = document.createElement('div');
    colum.classList.add('col-sm-7');


    let pathArray = window.location.pathname.split('/');
    let certificationEntityId = pathArray[4];

    const apiUrl = `http://uno.dev.certiffy.net:8000/rest/v1/requirement-certification?certification_entity=${certificationEntityId}`;

    if(!isNaN(certificationEntityId)){
        fetch(apiUrl)  // Cambia la URL a la de tu API
            .then(response => response.json())
            .then(data => {
                data.results.forEach(item => {
                    let nameLink = item.route ? `<a href="${item.route}" target="_blank" download>${item.name}</a>` : item.name;
                    let div = document.createElement('div');
                    div.classList.add('justify-content-center', 'align-items-center');
                    div.innerHTML = nameLink;

                    colum.appendChild(div);
                    
                    // let row = `<tr>
                    //     <td>${nameLink}</td>
                    // </tr>`;
                    // tbody.innerHTML += row;
                });
            })
            .catch(error => console.error("Error al obtener los datos:", error));
    } else {
        console.error("No se encontró un ID válido en la URL");
    }

    row.appendChild(colum);

    x.appendChild(row);
});