import PhoneInput from "react-phone-input-2";
import "react-phone-input-2/lib/bootstrap.css";
import Provider from "./FormInputs/Provider";
import Phone from "./FormInputs/Phone";

function ForgotForm({ I }) {
    return (

        <div className="center-container credential-form" >
            <div>Please enter your web10 provider and mobile number to recover your account.</div>
            <Provider I={I} />
            <Phone I={I} />

            <div className="field">
                <div className="control">
                    <button onClick={() => I.setMode("login")} className="button">Cancel</button>
                    <button
                        onClick={
                            () => {
                                I.setMode("appstore")
                                const [provider, username, password, betacode, retype] = [
                                    document.getElementById("provider").value,
                                    document.getElementById("username").value,
                                    document.getElementById("password").value,
                                    document.getElementById("betacode").value,
                                    document.getElementById("retypepass").value,
                                ];
                                I.recover(provider, I.phone)
                            }}
                        style={{ margin: "0px 10px" }}
                        className="button is-info"
                    >
                        Recover Account
                    </button>
                </div>
            </div>
        </div>
    );

}

export default ForgotForm;