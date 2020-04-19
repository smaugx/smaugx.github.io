// 获取网页不含域名的路径
var windowPath = window.location.pathname; 
// 图片信息文件路径
var imgDataPath = '/photos/photoslist.json'; 
// 图片显示数量
var imgMaxNum = 50; 
// 获取窗口宽度（以确定图片显示宽度）
var windowWidth = window.innerWidth
|| document.documentElement.clientWidth
|| document.body.clientWidth;
if (windowWidth < 768) {
    var imageWidth = 145; // 图片显示宽度(手机)
} else {
    var imageWidth = 215; // 图片显示宽度
}
// 腾讯云图片处理样式（根据图片显示宽度）
var imgStyle = '!' + imageWidth + 'x';


// 图片卡片（照片页面）
if (windowPath.indexOf('photos') > 0 ) {
    var LinkDataPath = imgDataPath;
    photo = {
        page: 1,
        offset: imgMaxNum,
        init: function () {
            var that = this;
            $.getJSON(LinkDataPath, function (data) {
                that.render(that.page, data);
            });
        },
        render: function (page, data) {
            var begin = (page - 1) * this.offset;
            var end = page * this.offset;
            if (begin >= data.length) return;
            var html, imgNameWithPattern, imgName, imageSize, imageX, imageY, li = "";
            for (var i = begin; i < end && i < data.length; i++) {
                imgNameWithPattern = data[i].split(';')[1];  // a.png
                imgName = imgNameWithPattern.split('.')[0]  // a
                imageSize = data[i].split(';')[0]; // length.height 
                imageX = imageSize.split('.')[0]; //  length
                imageY = imageSize.split('.')[1]; // height
							  
							  cdn_url       = data[i].split(';')[2]; // 原图 cdn url
							  small_cdn_url = data[i].split(';')[3]; // 缩略图 cdn url

                li += '<div class="card" style="width:' + imageWidth + 'px" >' +
                        '<div class="ImageInCard" style="height:'+ imageWidth * imageY / imageX + 'px">' +
                            '<a data-fancybox="gallery" href="' + cdn_url + '" data-caption="' + imgName + '" title="' +  imgName + '">' +
                                '<img data-src="' + small_cdn_url + '" src="' + small_cdn_url + '" data-loaded="true">' +
                            '</a>' +
                        '</div>' +
                      '</div>'
            }
            $(".MyGrid").append(li);
            this.minigrid();
        },
        minigrid: function() {
            var grid = new Minigrid({
                container: '.MyGrid',
                item: '.card',
                gutter: 12
            });
            grid.mount();
            $(window).resize(function() {
                grid.mount();
            });
        }
    }
    photo.init();
}
