// see stuff about a friend + friend group
// pictures, media , text about them. 
// also configure ( manage notifications / unfriend / unfollow )

import { R } from 'rectangles-npm'
import TopBar from '../shared/TopBar';
import SideBar from '../shared/SideBar';
import { Apps } from './Apps'

function AppStore({ I }) {
    return (
        <R root t bt bb br bl theme={I.theme}>
            <TopBar I={I}></TopBar>
            <R l tel>
                <SideBar I={I}></SideBar>
                <R t tel>
                    <Apps I={I}></Apps>
                    <div className="columns" style={{ width: "100%" }}>
                        <div className="column"></div>
                        <div className="column">
                            <div className="snippet" data-title=".dot-fire">
                                <div className="stage">
                                    <div className="dot-fire"></div>
                                    <br></br>
                                </div>
                            </div>
                        </div>
                    </div>
                </R>
            </R>
        </R>
    );
}

export default AppStore;
