function generate_electoral_list_match(contrato_id, data) {
    /**
     * Genera el HTML necesario para mostrar cuando ocurre un "matching" en las listas electorales
    **/
    let lista = "";
    for (d of data) {
        if (d.type == "person" && d.electoral_list != "") {
            lista += `<li><i class="fa fa-id-card" aria-hidden="true"></i>${d.name}
                <small class="text-muted">${d.electoral_lists}</small></li>`;
        }
    }
    let html = "No se encontraron coincidencias";
    if (lista.length > 0) {
        html = "<ul>"+lista+"</ul>"
    }
    $("#electoral-"+contrato_id+" p").html(html);
}


function generate_offshore_match(contrato_id, data) {
    /**
     * Genera el HTML necesario para mostrar cuando ocurre un "matching" en papeles offshore
    **/
    let lista = "";
    for (d of data) {
        if (d.panama_papers) {
            if (d.type == "person")
                lista += "<li><i class='fa fa-id-card' aria-hidden='true'></i>";
            else
                lista += "<li><i class='fa fa-building' aria-hidden='true'></i>";

            lista += d.name;
            lista += `<small class='text-muted'>Panama Papers
                <a href='https://es.wikipedia.org/wiki/Panama_Papers' target='_blank'>
                    <i class='fa fa-external-link' aria-hidden='true'></i>
                </a></small><i class='fa fa-id-card' aria-hidden='true'></i></li>`;
        }
    }

    let html = "No se encontraron coincidencias";
    if (lista.length > 0) {
        html = "<ul>"+lista+"</ul>"
    }
    $("#offshore-"+contrato_id+" p").html(html);
}



$(document).ready(function() {
    $(".need-search").on("click", function() {
        // Cuando se hace click en algún contrato adjudicado que no ha sido
        // buscado en librebor se busca en librebor
        contract_id = $(this).attr("contract-id");
        nif = $(this).attr("contract-nif");

        $.ajax({
            url: "/query?nif="+nif+"&contract="+contract_id,
            method: "GET",
            success: function(resp) {
                generate_electoral_list_match(contract_id, resp);
                generate_offshore_match(contract_id, resp);
            },
            error: function(resp) {
                generate_messages("Ha ocurrido un error interno. Recarga y vuelve a intentar", "warning");
            }
        }).always(function() {
            $(this).removeClass("need-search");
        });
    });
});
