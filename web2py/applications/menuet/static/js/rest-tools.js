/**
 * Created by Scorpa on 12/10/2017.
 */
function send_to_beck(url, DTO) {
    var data = JSON.stringify(DTO);
    $.ajax({
        type: 'POST',
        url: url,
        scriptCharset: "utf-8",
        contentType: "application/json; charset=utf-8",
        data: data,
        dataType: 'json',
        success: function (data) {
            window.alert(data['msg']);
        },
        error: function () {
            location.reload();
        }
    });
}



