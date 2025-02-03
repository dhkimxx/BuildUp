package main

import (
	"fmt"
	"log"
	"net/http"
	"strings"
)

func loginHandler(w http.ResponseWriter, r *http.Request) {
	fmt.Println(strings.Repeat("#", 100))
	fmt.Println(r)
	w.WriteHeader(http.StatusOK)
	// fmt.Fprintln(w, "{}")
}

func main() {
	http.HandleFunc("/", loginHandler)
	http.HandleFunc("/v2/", loginHandler)

	log.Println("Auth server started on port 8080")
	log.Fatal(http.ListenAndServe("0.0.0.0:8080", nil))

}
