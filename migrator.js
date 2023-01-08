const renderer = new DashRenderer();

(function(){
    const url = document.URL;

    const extensions = [
        "https://cdn.jsdelivr.net/npm/swiper@8/swiper-bundle.min.js",
        "https://cdn.jsdelivr.net/npm/echarts@5.4.1/dist/echarts.min.js",
        "/MLA/assets/view_dashboard.js",
        "/MLA/assets/view_dashboard_plots.js"
    ]

    const allowed_extensions = [
        "https://unpkg.com/dash.nprogress@latest/dist/dash.nprogress.js"
    ];
    const MLA_Prefixed = (page) => new RegExp(`^https?:\/\/.*\/MLA\/${page}`);

    if(
        MLA_Prefixed("view").test(url) || MLA_Prefixed("_test").test(url)
    ){
        allowed_extensions.push(extensions[0]);
        allowed_extensions.push(extensions[1]);
        allowed_extensions.push(extensions[2]);
        allowed_extensions.push(extensions[3]);
    }

    const head = document.getElementsByTagName('head')[0];


    allowed_extensions.forEach(function(scriptPath){
        const script = document.createElement('script');
        script.type = 'text/javascript';
        script.src = scriptPath;
        head.appendChild(script);
    });

})()
