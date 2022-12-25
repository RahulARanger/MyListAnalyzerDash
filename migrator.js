const renderer = new DashRenderer();

(function(){
    const url = document.URL;

    const extensions = [
        "https://cdn.jsdelivr.net/combine/npm/@splidejs/splide@4.1.4,npm/@splidejs/splide-extension-auto-scroll@0.5.3",
        "/MLA/assets/index.js"
    ]

    const allowed_extensions = [];
    const MLA_Prefixed = (page) => new RegExp(`^https?:\/\/.*\/MLA\/${page}`);

    if(
        MLA_Prefixed("view").test(url) || MLA_Prefixed("_test").test(url)
    ){
        allowed_extensions.push(extensions[0]);
        allowed_extensions.push(extensions[1]);
    }

    const head = document.getElementsByTagName('head')[0];


    allowed_extensions.forEach(function(scriptPath){
        const script = document.createElement('script');
        script.type = 'text/javascript';
        script.src = scriptPath;
        head.appendChild(script);
    });

})()
