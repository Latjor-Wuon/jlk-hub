// Simple Router for JLN Hub
export class Router {
    constructor() {
        this.routes = {};
        this.currentRoute = null;
        this.init();
    }

    init() {
        // Listen for hash changes
        window.addEventListener('hashchange', () => this.handleRouteChange());
        window.addEventListener('load', () => this.handleRouteChange());
    }

    register(path, handler) {
        this.routes[path] = handler;
    }

    navigate(path, params = {}) {
        let url = `#${path}`;
        const queryString = new URLSearchParams(params).toString();
        if (queryString) {
            url += `?${queryString}`;
        }
        window.location.hash = url;
    }

    handleRouteChange() {
        const hash = window.location.hash.slice(1); // Remove #
        const [path, queryString] = hash.split('?');
        const params = new URLSearchParams(queryString || '');
        
        const route = path || 'home';
        const handler = this.routes[route];
        
        if (handler) {
            const paramsObj = {};
            for (const [key, value] of params.entries()) {
                paramsObj[key] = value;
            }
            handler(paramsObj);
            this.currentRoute = route;
        } else {
            console.warn('Route not found:', route);
            this.navigate('home');
        }
    }

    getCurrentRoute() {
        return this.currentRoute;
    }

    getParams() {
        const hash = window.location.hash.slice(1);
        const [, queryString] = hash.split('?');
        const params = new URLSearchParams(queryString || '');
        const paramsObj = {};
        for (const [key, value] of params.entries()) {
            paramsObj[key] = value;
        }
        return paramsObj;
    }
}
