function init() {
    // console.log(data_now)
    var neo4jd3 = new Neo4jd3('#neo4jd3', {
        highlight: [
            {
                class: 'Project',
                property: 'name',
                value: 'neo4jd3'
            }, {
                class: 'Person',
                property: 'fb_id',
                value: 'eisman'
            }
        ],
        infoPanel: false,
        icons: {},
        labels: labels,
        minCollision: minCollision,
        neo4jData: data_now,
        nodeRadius: radius || 35,
        onNodeDoubleClick: function (node) {
            // console.log($('input[name="limit"]').val())
            $.ajax({
                type: 'POST',
                url: "/get-detail-data",
                data: {
                    'id': node.id,
                    'limit': $('input[name="limit"]').val() ? $('input[name="limit"]').val() : limit_generate
                },
                success: function (response) {
                    var new_data = JSON.parse(response)
                    new_data = check_existed_node_and_relationship(new_data)
                    if (new_data.results[0].data[0].graph.nodes.length == 0) {
                        showNotification('top', 'center', "Không tìm thấy dữ liệu nào phù hợp")
                    } else {
                        neo4jd3.updateWithNeo4jData(new_data)
                    }
                }
            })
        },
        onNodeClick: function (node) {
            // console.log(node)
            gen_info_panel_html(node)

        },
        onRelationshipDoubleClick: function (relationship) {
            console.log('double click on relationship: ' + JSON.stringify(relationship));
        },
        zoomFit: true
    });
}

// window.onload = init;

function gen_info_panel_html(node) {
    $('.profile-sidebar').empty()
    let html = '<div class="profile-sidebar">' +
        '                        <div class="profile-usertitle">' +
        '                            <div class="profile-usertitle-name">' + node.labels[0] + '</div>' +
        '                        </div>'
    let table ='<div class="profile-usermenu table-responsive">' +
        '<table class="table table-borderless table-hover table-striped table-light">' +
        '<tbody>'
    for (var k in node.properties) {
        if (node.properties.hasOwnProperty(k)) {
            table += ' <tr><td style="width: 30%"><strong>' + break_word(k) + '</strong></td><td>' + long_url(node, k) + '</td></tr>'
        }
    }
    // if (node.labels[0] === 'Person'){
    //     html += '<tr class="deep-learning"><td>Phân tích hành vi dựa vào Deep learning</td><td style="max-width: 30%">'+randomText()+'</td></tr>'
    // }
    table += '</tbody></table>'
    $('#div-modal-full-information').replaceWith(modal_full_infomation(node, table))
    html += table+'<button class="btn btn-primary btn-block" style="width: 50%; margin: auto" data-toggle="modal"' +
        ' data-target="#modal-full-information">See more</button></div></div>'

    $('.profile-sidebar').replaceWith(html)
}

function modal_full_infomation(node, table){
    console.log(node)
    let modal = '<div id="div-modal-full-information"><div class="modal fade" id="modal-full-information" tabindex="-1" role="dialog" aria-hidden="true">' +
        '    <div class="modal-dialog" role="document">' +
        '        <div class="modal-content">' +
        '            <div class="modal-header">' +
        '                <h4 class="modal-title"><strong>Detail Infomation</strong></h4>' +
        '                <button type="button" class="close" data-dismiss="modal" aria-label="Close">' +
        '                    <span aria-hidden="true">&times;</span>' +
        '                </button>' +
        '            </div>' +
        '            <div class="modal-body" style="margin: 0 0 0 6%;"><div class="lds-roller"><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div></div>' +
        '                <div class="row" style="overflow: scroll;"><div class="col-md-12>"' +
                    table + '</div>'+
        '                    <div class="col-md-12">'
    if (node.labels[0] == 'Person') {
        modal += '                        <label><button class="btn btn-load-more btn-success btn-block" style="display: block" ' +
        ' id="btn-more-info" data-id="'+node.id+'">More infomations</button></label>' +
        '                        '+
        '                        <div id="load-images">' +
            '                   </div>'+
        '                        <div id="load-status"></div>'+
        '                    '+
        '                        <div id="load-influencers"></div>'+
        '                    '
    }
    modal += '             </div></div></div><div class="modal-footer">' +
            '                <button type="button" class="btn btn-primary" data-dismiss="modal">Close</button>' +
            '            </div>' +
        '        </div></div>' +
        '    </div>' +
        '</div></div>'

    return modal
}

function randomText(){
    var list = ["Du lịch", "Thể thao", "Tài chính", "Sức khỏe", "Công nghệ"]
    return list[Math.floor(Math.random() * 4)]
}

function break_word(string) {
    return string.replace('_', ' ')
}

function long_url(node, k) {
    if (node.labels[0] == 'Life_Event' && k == 'fb_id') {
        return "<a href='https://facebook.com" + node.properties[k] + "' target='_blank'>Link</a>"
    }
    else if (node.labels[0] == 'Comment' && k == 'image') {
        return "<a href='" + node.properties[k] + "' target='_blank'>Link</a>"
    }
    else if (node.labels[0] == 'Status' && k == 'link_attachment' && node.properties[k].length > 0) {
        return "<a href='" + node.properties[k] + "' target='_blank'>Link</a>"
    }
    else if (node.labels[0] == 'Image' && (k == 'full_size_url' || k == 'temp_size_url') && node.properties[k].length > 0) {
        return "<a href='" + node.properties[k] + "' target='_blank'>" +
            "<img style='width: 100%' src='" + node.properties[k] + "' ></a>"
    }
    else {
        return node.properties[k]
    }
}

function check_existed_node_and_relationship(response_data) {
    var new_nodes = response_data.results[0].data[0].graph.nodes,
        new_relationship = response_data.results[0].data[0].graph.relationships,
        existed_nodes = data_now.results[0].data[0].graph.nodes,
        existed_relationship = data_now.results[0].data[0].graph.relationships,
        list_id_existed_nodes = [],
        list_id_existed_relationship = [],
        return_data = {
            "results": [
                {
                    "columns": [
                        "user",
                        "entity"
                    ],
                    "data": [
                        {
                            "graph": {
                                "nodes": [],
                                "relationships": []
                            }
                        }
                    ]
                }
            ],
            "errors": []
        }

    existed_nodes.forEach(function (e) {
        list_id_existed_nodes.push(e.id)
    });

    existed_relationship.forEach(function (e) {
        list_id_existed_relationship.push(e.id)
    });

    new_nodes.forEach(function (ele) {
        if (list_id_existed_nodes.indexOf(ele.id) < 0) {
            return_data.results[0].data[0].graph.nodes.push(ele)
            // data_now.results[0].data[0].graph.nodes.push(ele)
            existed_nodes.push(ele)
        }
    });

    new_relationship.forEach(function (ele) {
        if (list_id_existed_relationship.indexOf(ele.id) < 0) {
            return_data.results[0].data[0].graph.relationships.push(ele)
            // data_now.results[0].data[0].graph.relationships.push(ele)
            existed_relationship.push(ele)
        }
    });

    // console.log(data_now)
    return return_data
}

function contains(array, id) {
    var filter = array.filter(function (elem) {
        return elem.id === id;
    });

    return filter.length > 0;
}

$('body').on('click', 'button#btn-more-info',function () {
    $.ajax({
        url: '/get-more-infomation',
        method: 'POST',
        data:{
            'node_id': $('button#btn-more-info').data('id')
        },
        beforeSend: function(){
            $('#modal-full-information .modal-content').addClass('blur-background')
            $('.lds-roller').css('display','inline-block')
        },
        success: function(response) {
            $('#modal-full-information .modal-content').removeClass('blur-background')
            $('.lds-roller').css('display','none')
            if (response.ajax_status === 1) {
                var html_images= '<h2>Images</h2><div class="row">'
                $.each(response.images, function(index, value){
                    if (value[0].search('scontent') > -1){
                        html_images += '<div class="col-md-6 col-xs-6"><a href="'+value[0]+'" target="_blank" >' +
                        '<img style="width: 100%" src="'+value[0]+'">' +
                        '</a></div>'
                    }

                })
                $('#load-images').html(html_images+'</div>')

                var html_status = '<h2>Status</h2><table class="table table-responsive table-hover>"><thead><tr>' +
                    '      <th>Content</th>' +
                    '      <th>Style</th>' +
                    '      <th>Fb ID</th>' +
                    '      <th>Interaction</th>' +
                    '    </tr></thead><tbody></tbody>'
                $.each(response.status, function(index, value){
                    html_status += '<tr><td>'+value[0]+'</td><td>'+value[1]+'</td>' +
                        '<td>'+value[2]+'</td><td>'+value[3]+'</td></tr>'
                })
                $('#load-status').html(html_status+'</tbody></table>')

               var html_influencers = '<h2>Most interaction</h2><table class="table table-responsive table-hover>"><thead><tr>' +
                    '      <th>Name</th>' +
                    '      <th>Link</th>' +
                    '      <th>Number Interaction</th>' +
                    '    </tr></thead><tbody></tbody>'
                $.each(response.influencers, function(index, value){
                    html_influencers += '<tr><td>'+value[0]+'</td><td>'+value[1]+'</td><td>'+value[2]+'</td></tr>'
                })
                $('#load-influencers').html(html_influencers)
            } else {

            }
        }
    })
})