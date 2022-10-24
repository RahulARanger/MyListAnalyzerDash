(function (clickedToValidate, clickedToSearch, _asked, opened, stored, in_case, pipe_url){
    const ctx = dash_clientside.callback_context;
    const justRedirected = ctx?.triggered?.length > 0;
    const no_u = window.dash_clientside.no_update;

    
    if(ctx?.triggered && ctx.triggered[0]?.prop_id.includes("get-user-name")) return [no_u, true, no_u];

    const asked = (_asked ? _asked : (in_case === "---" ? "" : in_case)).toLowerCase();

    const note = {
        namespace:"dash_mantine_components",
        type:"Notification",
        props: {
            title:[
                "To Proceed Further,",
                {
                    props: {
                        children: new Date().toLocaleString(),
                        size: "xs"
                    },
                    namespace:"dash_mantine_components",
                    type: "Text"
                }
    
            ], id: "sample",
             message: ["Checking"], action: "show", autoClose: 2000,
             color: "orange", disallowClose: false
        }
    }

    if(!asked){
        note.props.message = ["Enter a UserName"]
        return [no_u, true, note];
    }
    
    const previous = (stored || "").toLowerCase();

    if(previous === asked) return [no_u, false, no_u]; // close the modal if name is same as previous ones

    console.log(ctx.triggered, asked, opened, stored, in_case, "asked", pipe_url);

    return no_u;
})