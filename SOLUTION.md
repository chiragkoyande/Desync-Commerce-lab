# Desync Cart Series / Author Solution

Keep this file out of the player handout.

## Boundary

Use a persistent HTTP/1.1 connection and compare the byte boundary each hop calculates. The frontend proxy checks the first request and forwards the connection. The backend consumes chunked framing and can parse leftover bytes as a second request.

## CL.TE

The frontend is length-oriented and the backend is transfer-oriented. The controlled replay sends both headers, ends a chunked body, and places `/internal/fulfillment` after it. The backend sees the mismatch, processes the secondary request, and releases `FLAG{cl_te}`.

## TE.CL

The lesson uses the reverse interpretation label and a separate protected route. The same local connection model demonstrates why choosing opposite framing rules produces a different boundary. It releases `FLAG{te_cl}` only when the matching lesson marker and secondary route are present.

## CL.0

A zero-length declared body leaves the next bytes on a reused connection to be interpreted as a new request. The local replay targets the CL.0 lesson route and releases `FLAG{cl_zero}` only after that connection condition.

## HTTP/2 downgrade

The lab does not expose a public HTTP/2 server or send traffic externally. The lesson models a gateway downgrade condition with an explicit local marker and a secondary request, then releases `FLAG{h2_desync}`. In a real gateway, the risk is at the HTTP/2-to-HTTP/1.1 translation boundary.

## Remediation

The patched proxy rejects conflicting framing before forwarding. Production systems should use one standards-compliant parser across every hop, normalize framing once, close ambiguous connections, and avoid proxy-only authorization assumptions.
