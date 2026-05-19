import csv
import random
from datetime import datetime, timedelta

def generate_data():
    # 1. Definir la estructura de Departamentos, Subdepartamentos y SKUs
    catalog = {
        "Electrónica": {
            "Cómputo": ["SKU-LAP-001", "SKU-MON-002", "SKU-TEC-003"],
            "Audio": ["SKU-AUD-004", "SKU-BOC-005"]
        },
        "Línea Blanca": {
            "Cocina": ["SKU-EST-006", "SKU-REF-007"],
            "Lavandería": ["SKU-LAV-008", "SKU-SEC-009"]
        },
        "Deportes": {
            "Calzado": ["SKU-TEN-010", "SKU-BOT-011"],
            "Accesorios": ["SKU-MOC-012", "SKU-BAL-013"]
        }
    }

    # Precios base y costos estimados por SKU para calcular ganancias realistas
    sku_details = {
        "SKU-LAP-001": {"precio": 12000, "costo": 8500},
        "SKU-MON-002": {"precio": 3500, "costo": 2200},
        "SKU-TEC-003": {"precio": 600, "costo": 350},
        "SKU-AUD-004": {"precio": 1500, "costo": 900},
        "SKU-BOC-005": {"precio": 2200, "costo": 1400},
        "SKU-EST-006": {"precio": 8000, "costo": 5500},
        "SKU-REF-007": {"precio": 15000, "costo": 10500},
        "SKU-LAV-008": {"precio": 11000, "costo": 7800},
        "SKU-SEC-009": {"precio": 9500, "costo": 6700},
        "SKU-TEN-010": {"precio": 1800, "costo": 1000},
        "SKU-BOT-011": {"precio": 2500, "costo": 1500},
        "SKU-MOC-012": {"precio": 800, "costo": 450},
        "SKU-BAL-013": {"precio": 450, "costo": 200}
    }

    # 2. Generar Campañas de Promoción
    # Campañas y sus rangos de fechas y descuentos
    promotions = [
        {"campaña": "Hot Sale", "inicio": "2026-03-05", "fin": "2026-03-15", "skus": ["SKU-LAP-001", "SKU-MON-002", "SKU-AUD-004"], "descuento": 0.15},
        {"campaña": "Buen Fin", "inicio": "2026-04-10", "fin": "2026-04-20", "skus": ["SKU-REF-007", "SKU-LAV-008", "SKU-TEN-010"], "descuento": 0.20},
        {"campaña": "Venta de Verano", "inicio": "2026-05-01", "fin": "2026-05-15", "skus": ["SKU-TEC-003", "SKU-BOC-005", "SKU-MOC-012", "SKU-BAL-013"], "descuento": 0.10}
    ]

    # Escribir promociones.csv
    with open("promociones.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["SKU", "Campaña", "Fecha Inicio", "Fecha Fin", "Descuento"])
        for p in promotions:
            for sku in p["skus"]:
                writer.writerow([sku, p["campaña"], p["inicio"], p["fin"], p["descuento"]])
    print("Archivo 'promociones.csv' generado con éxito.")

    # 3. Generar Ventas Diarias (90 días hacia atrás)
    end_date = datetime.strptime("2026-05-19", "%Y-%m-%d")
    start_date = end_date - timedelta(days=90)
    
    with open("ventas.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Fecha", "SKU", "Departamento", "Subdepartamento", "Venta", "Unidades", "Ganancia"])
        
        current_date = start_date
        while current_date <= end_date:
            date_str = current_date.strftime("%Y-%m-%d")
            
            # Decidir cuántas transacciones ocurren hoy (entre 5 y 15)
            num_sales = random.randint(5, 15)
            
            for _ in range(num_sales):
                # Seleccionar un depto, subdepto y sku aleatorio
                depto = random.choice(list(catalog.keys()))
                subdepto = random.choice(list(catalog[depto].keys()))
                sku = random.choice(catalog[depto][subdepto])
                
                details = sku_details[sku]
                precio_base = details["precio"]
                costo_base = details["costo"]
                
                # Revisar si el SKU está en promoción en esta fecha
                descuento = 0.0
                for p in promotions:
                    p_start = datetime.strptime(p["inicio"], "%Y-%m-%d")
                    p_end = datetime.strptime(p["fin"], "%Y-%m-%d")
                    if sku in p["skus"] and p_start <= current_date <= p_end:
                        descuento = p["descuento"]
                        break
                
                # Aplicar descuento si aplica
                precio_venta = precio_base * (1.0 - descuento)
                
                # Cantidad de unidades vendidas (durante la promo se vende más)
                if descuento > 0:
                    unidades = random.randint(2, 6)
                else:
                    unidades = random.randint(1, 3)
                
                # Calcular ingresos (Venta) y ganancias
                ingresos = round(precio_venta * unidades, 2)
                costo_total = costo_base * unidades
                ganancia = round(ingresos - costo_total, 2)
                
                writer.writerow([date_str, sku, depto, subdepto, ingresos, unidades, ganancia])
            
            current_date += timedelta(days=1)
    print("Archivo 'ventas.csv' generado con éxito.")

if __name__ == "__main__":
    generate_data()
