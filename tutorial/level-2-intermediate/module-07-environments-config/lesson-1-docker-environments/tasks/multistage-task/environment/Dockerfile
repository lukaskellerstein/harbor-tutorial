# Multi-stage Dockerfile
# Demonstrates: build stage compiles Go, runtime stage is minimal
# This produces a much smaller final image.

# ---- Build stage ----
FROM golang:1.22-alpine AS builder

WORKDIR /build

# Create a simple Go program.
#
# Written with printf rather than a shell heredoc: the Dockerfile parser ends a
# RUN instruction at the newline, so a heredoc body would be read as further
# Dockerfile instructions ("package main" is not one) and the build would fail.
RUN printf '%s\n' \
        'package main' \
        '' \
        'import "fmt"' \
        '' \
        'func main() {' \
        '    fmt.Println("Hello from a multi-stage Docker build!")' \
        '    fmt.Println("This binary was compiled in the builder stage")' \
        '    fmt.Println("but runs in a minimal runtime stage.")' \
        '}' \
        > main.go

# Compile a static binary
RUN CGO_ENABLED=0 GOOS=linux go build -o greeter main.go

# ---- Runtime stage ----
FROM alpine:3.20

# Only install what is needed at runtime
RUN apk add --no-cache bash

WORKDIR /app

# Copy just the compiled binary from the build stage
COPY --from=builder /build/greeter /app/greeter
RUN chmod +x /app/greeter
