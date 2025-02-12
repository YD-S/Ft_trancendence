import { PageManager } from "./page-manager.js";
import { saveToken } from "./utils.js";
import {Notification} from "./notification.js";

export function login() {
	let username = document.getElementById("username").value.trim();
	let password = document.getElementById("password").value;
	let data = {
		username: username.trim(),
		password: password,
	};
	fetch("/api/auth/login/", {
		method: "POST",
		headers: {
			"Content-Type": "application/json",
		},
		body: JSON.stringify(data),
	})
		.then((response) => {
			if (response.status >= 400) {
				throw new Error("AUTH.ERROR.INVALID_CREDENTIALS");
			}
			return response.json();
		})
		.then((data) => {
			if (data.action === "2fa") {
				PageManager.getInstance().load(`auth/2fa`, false, { args: [data.email2fa, data.user_id] });
			} else if (data.action === "login") {
				saveToken(data);
				PageManager.getInstance().load("home");
			}
		})
		.catch((error) => {
			Notification.error(error.message);
		});
}

function oauth() {
	fetch("/api/auth/oauth/")
		.then((response) => {
			if (response.status >= 400) {
				throw new Error("AUTH.ERROR.FAILED_OAUTH");
			}
			return response.json();
		})
		.then((data) => {
			sessionStorage.setItem("oauth_state", data.state);
			window.location.href = data.url;
		})
		.catch((error) => {
			Notification.error(error.message);
		});
}

PageManager.getInstance().setOnPageLoad("auth/login", () => {
	document.getElementById("submit").addEventListener("click", (event) => {
		login();
	});
	// if enter key is pressed while in the password or username field, login
	document.getElementById("password").addEventListener("keyup", (event) => {
		if (event.key === "Enter") {
			login();
		}
	});
	document.getElementById("username").addEventListener("keyup", (event) => {
		if (event.key === "Enter") {
			login();
		}
	});
	document.getElementById("oauth").addEventListener("click", (event) => {
		oauth();
	});
});
