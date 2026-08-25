# syntax=docker/dockerfile:1
FROM golang:1.27-alpine AS build
WORKDIR /src
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 go build -trimpath -o /out/event-gateway ./cmd/event-gateway

FROM gcr.io/distroless/static-debian12:nonroot
COPY --from=build /out/event-gateway /event-gateway
USER nonroot:nonroot
EXPOSE 8080
ENTRYPOINT ["/event-gateway"]
