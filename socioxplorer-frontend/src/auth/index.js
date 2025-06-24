import {createAuthProvider} from 'react-token-auth';


export const [useAuth, authFetch, login, logout] =
    createAuthProvider({
        accessTokenKey: 'accessToken',
        onUpdateToken: (token) => fetch('/api/refresh', {
            method: 'POST',
            header: {'Content-Type': 'application/json'},
            body: JSON.stringify(token)
        })
        .then(r => r.json())
    });