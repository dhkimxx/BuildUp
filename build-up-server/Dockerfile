FROM golang:1.23

WORKDIR /build-up-server

COPY go.mod go.sum ./
RUN go mod download

COPY *.go ./

RUN CGO_ENABLED=0 GOOS=linux go build -o build-up-server

EXPOSE 8080

CMD ["./build-up-server"]