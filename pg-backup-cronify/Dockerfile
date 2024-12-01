FROM golang:latest AS builder

WORKDIR /app

# just copying main script is enough
# it does not have any 3-rd party deps
COPY go.mod main.go .

RUN go build -o main .

FROM postgres AS final

RUN apt-get update && apt-get install -y ca-certificates

WORKDIR /app

COPY --from=builder /app/main /app/main

CMD ["/app/main"]