# immc_orders

Contains the order manager node.

## Interfaces

### 'pending_orders' service

Request:
`$ rosservice call /pending_orders "{}"`

Response (example)

    id: 1
    objects: 
      - red_cube
      - blue_cube
    desired_location: 
      x: -1.0
      y: -4.67
      z: 0.0

### 'submit_order' service

Request (example)
`$ rosservice call /submit_order "order_id: 1"`

Response (example)

    True
