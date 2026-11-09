# PopUpOps — Event Equipment & Operations (Odoo 17)

An **independent, fictional learning project**, designed to demonstrate Odoo addon development with a different business domain from employer projects.

**Status:** Milestone 1 (prototype). The code has been syntax-checked but has **not** been installed against a live Odoo instance in this repository's build environment.

## Current features

- Event bookings with customers (Odoo Contacts / `res.partner`), venue, dates, event type and coordinator
- Event equipment and service lines referencing Odoo products
- Computed estimated total and generated booking reference
- Workflow: Draft → Confirmed → Ready for Setup → Completed (or Cancelled)
- Draft Sales quotation creation from a confirmed booking; opens in Odoo Sales
- Chatter tracking, search, filters, global company record rules and internal-user ACLs
- Optional fictional demo records and Odoo `TransactionCase` tests

**Not implemented yet:** actual inventory reservation, fleet assignments, rental availability, customer portal, dispatch, invoices/payment automation, and dashboards. An estimate is not a financial invoice, and creating a quotation does not reserve stock.

## Prerequisites

- Odoo **17.0** (Community-compatible addon)
- PostgreSQL and a working Odoo 17 server
- Odoo addons `mail` and `sale_management` (installed automatically as module dependencies)
- User account with internal access. **Creating a Sales quotation additionally requires normal Odoo Sales permissions.**

## Installation on macOS / VS Code

1. Extract the folder **`popup_ops`** into:

   ```text
   /Users/nomsa/Desktop/Development/odoo-17.0/custom_addons/popup_ops
   ```

2. Open the Odoo source root in VS Code and use its terminal:

   ```bash
   cd /Users/nomsa/Desktop/Development/odoo-17.0
   source .venv/bin/activate
   ```

3. Start PostgreSQL if needed:

   ```bash
   brew services start postgresql@16
   ```

4. Start Odoo, using **both** your normal addons folder and custom folder:

   ```bash
   python odoo-bin --addons-path=addons,custom_addons --http-port=8069
   ```

5. In your local test database, go to **Apps**, remove the default Apps filter if needed, and select **Update Apps List** (Developer Mode may be required). Search for **PopUpOps - Event Operations** and select **Install**. Its `sale_management` dependency may add Sales if not already installed.

   **Alternative CLI install** (use the actual database name from your local database; stop an existing Odoo process first):

   ```bash
   python odoo-bin --addons-path=addons,custom_addons -d YOUR_TEST_DB -i popup_ops --stop-after-init
   ```

6. Restart the server normally and open the **PopUpOps → Event Bookings** menu.

### First guided exercise

1. In **Contacts**, make a fictional customer, e.g. `Fictional: BrightSky Events`.
2. In **Sales → Products**, make a saleable service, e.g. `Event Chair Rental (per event)`, at a sample unit price.
3. In **PopUpOps → Event Bookings → New**, fill event details and add the product line.
4. Save, then select **Confirm → Create Quotation**. Open the generated draft quotation in Sales.
5. Return to the booking, select **Ready for Setup → Complete**.
6. Inspect the Python `models/` and XML `views/` files in VS Code to connect each field/button to its implementation.

## Running tests

From your Odoo 17 source root (change `YOUR_TEST_DB`):

```bash
source .venv/bin/activate
python odoo-bin --addons-path=addons,custom_addons -d YOUR_TEST_DB -u popup_ops --test-tags /popup_ops --stop-after-init
```

Do not run against production. Tests can create records in the test database and may take some time to run. Installation with `--test-enable` is also supported.

## Developing further

See [ROADMAP.md](ROADMAP.md). When editing XML or Python models, restart Odoo and **upgrade** the installed module (`-u popup_ops` or Apps → Upgrade) as appropriate.

## Repository layout

```text
popup_ops/
├── __manifest__.py          # App metadata and dependencies
├── models/                  # Odoo ORM models and business methods
├── views/                   # XML forms, list, searches, menus and actions
├── security/                # Access rights and company record rules
├── data/                    # Booking-number sequence
├── demo/                    # Optional fictional sample data
├── tests/                   # Odoo TransactionCase tests
├── ROADMAP.md
└── README.md
```

## Independence and privacy

This module, its business rules and sample data are original practice material. **Do not commit** proprietary ZiWaste code, screenshots, infrastructure diagrams, private documents, credentials, customer details or real databases to this public repository.

## License

LGPL-3.0-only (see `LICENSE`). Odoo itself remains subject to its own licenses.
