---
### Bla

```go
package main

import (
	"fmt"
	"golang.org/x/net/websocket"
	"log"
	"net/http"
)

func echoHandler(ws *websocket.Conn) {
	msg := make([]byte, 512)
	n, err := ws.Read(msg)
	if err != nil {
		log.Fatal(err)
	}
	fmt.Printf("Receive: %s\n", msg[:n])

	m, err := ws.Write(msg[:n])
	if err != nil {
		log.Fatal(err)
	}
	fmt.Printf("Send: %s\n", msg[:m])
}
```


@[1]
@[3-8]
@[10-24]
