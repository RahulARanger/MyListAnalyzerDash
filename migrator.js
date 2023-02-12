const renderer = new DashRenderer();

(function(){
    const url = document.URL;
    const modules = {
        swiper: ["https://cdn.jsdelivr.net/npm/swiper@8/swiper-bundle.min.js"],
        eCharts: ["https://cdn.jsdelivr.net/npm/echarts@5.4.1/dist/echarts.min.js", "https://cdn.jsdelivr.net/combine/npm/echarts@5.4.1/theme/dark-digerati.min.js,npm/echarts@5.4.1/theme/azul.min.js,npm/echarts@5.4.1/theme/bee-inspired.min.js,npm/echarts@5.4.1/theme/blue.min.js,npm/echarts@5.4.1/theme/caravan.min.js,npm/echarts@5.4.1/theme/carp.min.js,npm/echarts@5.4.1/theme/cool.min.js,npm/echarts@5.4.1/theme/dark.min.js,npm/echarts@5.4.1/theme/dark-blue.min.js,npm/echarts@5.4.1/theme/dark-bold.min.js,npm/echarts@5.4.1/theme/dark-fresh-cut.min.js,npm/echarts@5.4.1/theme/dark-mushroom.min.js,npm/echarts@5.4.1/theme/eduardo.min.js,npm/echarts@5.4.1/theme/forest.min.js,npm/echarts@5.4.1/theme/fresh-cut.min.js,npm/echarts@5.4.1/theme/fruit.min.js,npm/echarts@5.4.1/theme/gray.min.js,npm/echarts@5.4.1/theme/green.min.js,npm/echarts@5.4.1/theme/helianthus.min.js,npm/echarts@5.4.1/theme/infographic.min.js,npm/echarts@5.4.1/theme/inspired.min.js,npm/echarts@5.4.1/theme/jazz.min.js,npm/echarts@5.4.1/theme/london.min.js,npm/echarts@5.4.1/theme/macarons.min.js,npm/echarts@5.4.1/theme/macarons2.min.js,npm/echarts@5.4.1/theme/vintage.min.js,npm/echarts@5.4.1/theme/tech-blue.min.js,npm/echarts@5.4.1/theme/shine.min.js,npm/echarts@5.4.1/theme/sakura.min.js,npm/echarts@5.4.1/theme/royal.min.js,npm/echarts@5.4.1/theme/roma.min.js,npm/echarts@5.4.1/theme/red-velvet.min.js,npm/echarts@5.4.1/theme/red.min.js,npm/echarts@5.4.1/theme/mint.min.js"],
        userView: ["/MLA/assets/view_dashboard.js", "/MLA/assets/view_dashboard_plots.js"]}

    // Maintain the scripts based on the order
    const allowed_extensions = ["https://unpkg.com/dash.nprogress@latest/dist/dash.nprogress.js"];
    const MLA_Prefixed = (page) => new RegExp(`^https?:\/\/.*\/MLA\/${page}`);

    if(MLA_Prefixed("view").test(url) || MLA_Prefixed("_test").test(url))
        allowed_extensions.push(...modules.swiper, ...modules.eCharts, ...modules.userView); 

    
    const head = document.getElementsByTagName('head')[0];
    allowed_extensions.forEach(function(scriptPath){
        const script = document.createElement('script');
        script.type = 'text/javascript'; script.src = scriptPath;
        head.appendChild(script);
    });
})()
