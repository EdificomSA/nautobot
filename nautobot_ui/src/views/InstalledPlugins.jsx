import NautobotTable from "@components/core/Table";
import BaseLayout from "@components/layouts/BaseLayout";
import ListTemplate from "@layouts/ListTemplate";

export default function InstalledPlugins(){
    return (
        <ListTemplate
            page_title={"Installed Plugins"}
            table_head_url="plugins/installed-plugins/table-fields/"
            table_data_url="plugins/installed-plugins/"
            buttons={[
                {"icon": "home", "link": "#", "tooltip": "Plugin home"},
                {"icon": "cog", "link": "#", "tooltip": "Settings"},
                {"icon": "book", "link": "#", "tooltip": "Plugin details"},
            ]}
        />
    )
}