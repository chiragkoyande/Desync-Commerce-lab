# Architecture Notes

The Next.js service is the normal storefront and challenge UI. Burp traffic is sent to the separate teaching proxy on port 8080. The proxy forwards to a private backend over the Compose network. The backend owns challenge state and the flag.

The proxy is deliberately small and deterministic so the lab does not depend on implementation quirks in a production proxy version. It is a local teaching reverse proxy, not a general-purpose proxy and it cannot target arbitrary hosts.
