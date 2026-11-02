# Project 04 — Hybrid Cloud Connectivity with Transit Gateway and Site-to-Site VPN

**Architecture:** Hybrid networking / hub and spoke  
**Goal:** Connect multiple AWS VPCs to an on-premises network through a central Transit Gateway.

## Target architecture

~~~mermaid
flowchart LR
    OnPrem[On-premises network / VPN peer] <-->|IPsec + BGP| TGW[Transit Gateway]
    TGW <--> DEV[Development VPC]
    TGW <--> STG[Staging VPC]
    TGW <--> PROD[Production VPC]
    OnPrem -. DNS queries .-> Resolver[Route 53 Resolver]
    Resolver <--> VPCDNS[Private hosted zones]
~~~

## Phase 1 — IP plan and prerequisites

1. Choose a Region and three VPC CIDR blocks that do not overlap with one another or the on-premises network.
2. Define which environments may communicate; default to no inter-environment access.
3. Select an on-premises VPN device or lab router/firewall that supports IPsec and preferably BGP.
4. Record the customer gateway public IP and BGP ASN.
5. Decide whether to use a real VPN peer or a clearly labeled simulation. A Transit Gateway VPN needs an actual customer gateway peer to establish tunnels.

## Phase 2 — VPC spokes

1. Create separate Dev, Staging, and Prod VPCs.
2. Create private subnets and route tables in each VPC.
3. Create application security groups with only required inbound rules.
4. Enable VPC DNS support and hostnames.
5. Deploy small test endpoints only if needed.
6. Keep environment CIDRs and security policies in configuration.

## Phase 3 — Transit Gateway

1. Create a Transit Gateway with an explicit ASN and DNS support as required.
2. Create separate Transit Gateway route tables for environment segmentation.
3. Attach each VPC using dedicated attachment subnets.
4. Associate each attachment with the intended route table.
5. Propagate only required routes.
6. Add explicit static routes or route propagation based on the segmentation design.
7. Update VPC route tables to point approved remote CIDRs to Transit Gateway.

**Checkpoint:** VPC attachments are available and route tables contain only approved paths.

## Phase 4 — Site-to-Site VPN

1. Create a Customer Gateway resource with peer public IP and ASN.
2. Create a Transit Gateway VPN attachment.
3. Download the AWS-generated vendor configuration.
4. Configure the on-premises device with both IPsec tunnels, IKE settings, inside tunnel addressing, and BGP peers.
5. Use BGP for dynamic route exchange where supported.
6. Verify tunnel state and BGP route learning.
7. Test connectivity in both directions with matching security-group and firewall rules.

Do not expose a test instance to all internet traffic for troubleshooting. Use narrow temporary rules and remove them.

## Phase 5 — Hybrid DNS

1. Create a private hosted zone for an internal lab domain.
2. Associate it with required VPCs.
3. Create Route 53 Resolver inbound endpoints for on-premises-to-AWS DNS queries.
4. Create outbound endpoints and forwarding rules for AWS-to-on-premises queries.
5. Configure conditional forwarding on on-premises DNS servers.
6. Test name resolution in both directions.

## Phase 6 — Multi-account and inspection

1. Use AWS RAM to share Transit Gateway with another lab account only when required.
2. Accept the share and attach the additional VPC.
3. Add Network Firewall after basic routing works.
4. Route selected traffic through inspection endpoints.
5. Enable CloudTrail and AWS Config recording for audit evidence.

## Phase 7 — Validation

- All VPC attachments are available.
- Only approved CIDR routes are propagated.
- VPN tunnels establish and BGP routes are learned.
- Dev cannot reach Prod unless explicitly allowed.
- DNS resolves in both directions for approved zones.
- Firewall logs show test traffic.
- Tunnel failure and recovery behavior is documented.

## Cost and cleanup

Transit Gateway, VPN, Resolver endpoints, and Network Firewall incur ongoing or usage-based charges. Deploy for a short lab window. Remove Network Firewall resources, Resolver endpoints/rules, VPN attachment, Customer Gateway, VPC attachments, Transit Gateway, and VPC resources in dependency order. Confirm no hourly networking resources remain.

## Definition of done

A documented hub-and-spoke design routes only approved prefixes; VPN/BGP is demonstrated with a real peer or clearly labeled simulation; and hybrid DNS is tested.
