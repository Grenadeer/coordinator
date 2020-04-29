
function getData(data) {
    var str = "data=" + data;
    $.ajax({
        url: '/record/json/list/',
        type: 'get',
        data: str,
        dataType: 'json',
        error: function (data) {
            $('#record_table').html('Не удалось получить данные от сервера.');
        },
        success: function (data) {
            let rows = '<table class="table">';
            rows += `
                <tr>
                    <th>Подразделение</th>
                    <th>Адрес</th>
                    <th>Пациент</th>
                    <th>Врач</th>
                    <th>Статус</th>
                </tr>
            `;
            if (data.records.length == 0) {
                rows += `
                <tr>
                    <td colspan=3 class="text-center">Нет совпадений</td>
                </tr>`;
            }
            data.records.forEach(record => {
                rows += `
                <tr>
                    <td>${record.department__name}</td>
                    <td>${record.address_street} ${record.address_building}-${record.address_apartment}</td>
                    <td>${record.patient}</td>
                    <td>${record.doctor__name}</td>
                    <td>
                        ${record.service_type__name}
                    </td>
                </tr>`;}
                );
            rows += '</table>';
            $('#record_table').html(rows);
        }
    });
}
