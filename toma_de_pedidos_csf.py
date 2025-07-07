import streamlit as st

import pandas as pd

from datetime import datetime

import os

import re

from st_copy_to_clipboard import st_copy_to_clipboard



# --- Configuration for the consecutive number ---

CONSECUTIVE_FILE = 'ultimo_consecutivo.txt'

INITIAL_CONSECUTIVE = 1000



def get_next_consecutive():

    """Reads the last consecutive number from a file, increments it, and saves it back.

    This function should only be called when a *new* order is being finalized."""

    current_consecutive = INITIAL_CONSECUTIVE

    if os.path.exists(CONSECUTIVE_FILE):

        try:

            with open(CONSECUTIVE_FILE, 'r') as f:

                content = f.read().strip()

                if content:

                    current_consecutive = int(content)

                else:

                    st.warning(f"Advertencia: El archivo '{CONSECUTIVE_FILE}' está vacío. Reiniciando consecutivo a {INITIAL_CONSECUTIVE}.")

                    current_consecutive = INITIAL_CONSECUTIVE

        except ValueError:

            st.warning(f"Advertencia: El archivo '{CONSECUTIVE_FILE}' contiene un valor inválido. Reiniciando consecutivo a {INITIAL_CONSECUTIVE}.")

            current_consecutive = INITIAL_CONSECUTIVE

    

    next_consecutive = current_consecutive + 1

    with open(CONSECUTIVE_FILE, 'w') as f:

        f.write(str(next_consecutive))

    

    return next_consecutive



# Initialize the file if it doesn't exist on first run

if not os.path.exists(CONSECUTIVE_FILE):

    with open(CONSECUTIVE_FILE, 'w') as f:

        f.write(str(INITIAL_CONSECUTIVE))



# --- 1. Datos de los productos ---

# Original list, now specifically for products primarily sold by boxes/cases

# Entries that are now explicitly in 'productos_data_unidades' have been removed or modified here.

productos_data_cajas = [

    # These remain in cajas because their primary sale is by full cases,

    # or the 'X units / CAJA X Y' structure is best for 'cajas' list.

    {"COD_PRODUCTO": "DDPHCO0010", "DESCRIPCION": "DERMADIVA CON COLAGENO X 10 UNIDAD / CAJA X 48", "UNIDAD_X_PAQUETE": 10, "UNIDAD_X_CAJA": 48},

    {"COD_PRODUCTO": "DDPHPE0001", "DESCRIPCION": "DERMADIVA CON PEPINO X 10UNIDAD / CAJA X 48", "UNIDAD_X_PAQUETE": 10, "UNIDAD_X_CAJA": 48},

    {"COD_PRODUCTO": "DDPHSR0010", "DESCRIPCION": "DERMADIVA CON ROSAS Y ALOE VERA X 10 UNIDAD / CAJA X 48", "UNIDAD_X_PAQUETE": 10, "UNIDAD_X_CAJA": 48},

    {"COD_PRODUCTO": "DDPHBA0010", "DESCRIPCION": "TOALLA DESMAQUILLANTE DERMADIVA X 10-48 SURTIDA", "UNIDAD_X_PAQUETE": 10, "UNIDAD_X_CAJA": 48},

    {"COD_PRODUCTO": "#N/D_AMTOCOL30", "DESCRIPCION": "AMARRE TO. DESMAQUILLANTES FACE CLEAN COLAGENO X 30 / CAJA X 24", "UNIDAD_X_PAQUETE": 30, "UNIDAD_X_CAJA": 24},

    {"COD_PRODUCTO": "#N/D_AMTOMIX30", "DESCRIPCION": "AMARRE TO. DESMAQUILLANTES FACE CLEAN MIXTA X 30 / CAJA X 24 UN", "UNIDAD_X_PAQUETE": 30, "UNIDAD_X_CAJA": 24},

    {"COD_PRODUCTO": "#N/D_AMTOPEP30", "DESCRIPCION": "AMARRE TO. DESMAQUILLANTES FACE CLEAN PEPINO X 30 / CAJA X 24 U", "UNIDAD_X_PAQUETE": 30, "UNIDAD_X_CAJA": 24},

    {"COD_PRODUCTO": "#N/D_AMTORO30", "DESCRIPCION": "AMARRE TO. DESMAQUILLANTES FACE CLEAN ROSAS Y ALOE VERA X 30 / CAJA X 24", "UNIDAD_X_PAQUETE": 30, "UNIDAD_X_CAJA": 24},

    {"COD_PRODUCTO": "SWPHSA0050", "DESCRIPCION": "TOALLAS HUMEDAS SENIORS WIPES X 50 / CAJA X 12 UND", "UNIDAD_X_PAQUETE": 50, "UNIDAD_X_CAJA": 12},

    {"COD_PRODUCTO": "FKPHSA0010", "DESCRIPCION": "PAÑITOS HÚMEDOS FRESKITOS X 10 / CAJA X 48", "UNIDAD_X_PAQUETE": 10, "UNIDAD_X_CAJA": 48},

    {"COD_PRODUCTO": "FKPHSA0025", "DESCRIPCION": "PAÑITOS HÚMEDOS FRESKITOS X 25 / CAJA X 48 UND", "UNIDAD_X_PAQUETE": 25, "UNIDAD_X_CAJA": 48},

    {"COD_PRODUCTO": "FTPHSA0040", "DESCRIPCION": "PAÑITOS HÚMEDOS FRESKITOS X 40 / CAJA X 36 UND", "UNIDAD_X_PAQUETE": 40, "UNIDAD_X_CAJA": 36},

    {"COD_PRODUCTO": "FTPHSA0102", "DESCRIPCION": "PAÑITOS HÚMEDOS FRESKITOS X 102 / CAJA X 12 UND", "UNIDAD_X_PAQUETE": 102, "UNIDAD_X_CAJA": 12},

    {"COD_PRODUCTO": "FTPHSA0105", "DESCRIPCION": "PAÑITOS HÚMEDOS FRESKITOS X 105 / CAJA X 24 UND", "UNIDAD_X_PAQUETE": 105, "UNIDAD_X_CAJA": 24},

    # FGPHSA001 is now primarily in unidades list (as X1 unit), so this one is for the larger cases of X10 and X15.

    {"COD_PRODUCTO": "FGPHSA0010", "DESCRIPCION": "PAÑITOS HÚMEDOS ED ESPECIAL NEGRO X10 / CAJA X 48", "UNIDAD_X_PAQUETE": 10, "UNIDAD_X_CAJA": 48},

    {"COD_PRODUCTO": "FGPHSA0015", "DESCRIPCION": "PAÑITOS HÚMEDOS ED ESPECIAL NEGRO X15 / CAJA X 30", "UNIDAD_X_PAQUETE": 15, "UNIDAD_X_CAJA": 30},

    

    {"COD_PRODUCTO": "#N/D_DMWP5KG", "DESCRIPCION": "DETERGENTE MAXI WASH PLUS X 5 KG / BULTO X 4", "UNIDAD_X_PAQUETE": 5, "UNIDAD_X_CAJA": 4},

    {"COD_PRODUCTO": "#N/D_DMWP2KG", "DESCRIPCION": "DETERGENTE MAXI WASH PLUS X 2 KG / BULTO X 10", "UNIDAD_X_PAQUETE": 2, "UNIDAD_X_CAJA": 10},

    {"COD_PRODUCTO": "MWHTAO1000", "DESCRIPCION": "DETERGENTE MAXI WASH PLUS X 1 KG / BULTO X 20 UND", "UNIDAD_X_PAQUETE": 1, "UNIDAD_X_CAJA": 20},

    {"COD_PRODUCTO": "#N/D_DMWMA1KG", "DESCRIPCION": "DETERGENTE MAXI WASH MULTIUSOS X 1 KG / BULTO X 20 UND", "UNIDAD_X_PAQUETE": 1, "UNIDAD_X_CAJA": 20},

    {"COD_PRODUCTO": "#N/D_DMWMA2KG", "DESCRIPCION": "DETERGENTE MAXI WASH MULTIUSOS X 2 KG / BULTO X 10 UND", "UNIDAD_X_PAQUETE": 2, "UNIDAD_X_CAJA": 10},

    {"COD_PRODUCTO": "ANEBMF0300", "DESCRIPCION": "ENJUAGUE BUCAL ACTIVMINT MENTA FRESCA X 300ML / CAJA X 15 UN", "UNIDAD_X_PAQUETE": 300, "UNIDAD_X_CAJA": 15},

    {"COD_PRODUCTO": "#N/D_EBMF500", "DESCRIPCION": "ENJUAGUE BUCAL ACTIVMINT MENTA FRESCA X 500ML / CAJA X 15 UN", "UNIDAD_X_PAQUETE": 500, "UNIDAD_X_CAJA": 15},

    {"COD_PRODUCTO": "ANEBYB0300", "DESCRIPCION": "ENJUAGUE BUCAL ACTIVMINT YERBABUENA 300ML / CAJA X 15 UND", "UNIDAD_X_PAQUETE": 300, "UNIDAD_X_CAJA": 15},

    {"COD_PRODUCTO": "#N/D_EBYB500", "DESCRIPCION": "ENJUAGUE BUCAL ACTIVMINT YERBABUENA 500ML / CAJA X 15 UND", "UNIDAD_X_PAQUETE": 500, "UNIDAD_X_CAJA": 15},

    {"COD_PRODUCTO": "FKCRLB0012", "DESCRIPCION": "CREMA HUMECTANTE FRESKITOS MANOS Y CUERPO X 800ML / CAJA X 12", "UNIDAD_X_PAQUETE": 800, "UNIDAD_X_CAJA": 12},

    {"COD_PRODUCTO": "#N/D_JLAB1000", "DESCRIPCION": "JABON LIQUIDO AVENA X 1000 ML / CAJA X 16", "UNIDAD_X_PAQUETE": 1000, "UNIDAD_X_CAJA": 16},

    {"COD_PRODUCTO": "FKJLFR1000", "DESCRIPCION": "JABON LIQUIDO FRESKITOS FRUTOS ROJOS X 1L / CAJA X 16 UND", "UNIDAD_X_PAQUETE": 1000, "UNIDAD_X_CAJA": 16},

    {"COD_PRODUCTO": "FKJLMV1000", "DESCRIPCION": "JABON LIQUIDO FRESKITOS MANZANA VERDE X 1L / CAJA X 16 UND", "UNIDAD_X_PAQUETE": 1000, "UNIDAD_X_CAJA": 16},

    {"COD_PRODUCTO": "FPPNMC050", "DESCRIPCION": "PAÑITOS HUMEDOS FRESKISPETS X 50 / CAJA X 48 UND", "UNIDAD_X_PAQUETE": 50, "UNIDAD_X_CAJA": 48},

    {"COD_PRODUCTO": "FKSHAL0800", "DESCRIPCION": "SHAMPOO FRESKITOS ALOE Y MANZANILLA X 500 ML / CAJA X 24 UND", "UNIDAD_X_PAQUETE": 500, "UNIDAD_X_CAJA": 24},

    {"COD_PRODUCTO": "FKSHMA0800_24", "DESCRIPCION": "SHAMPOO FRESKITOS MANZANILLA X 800 ML / CAJA X 24 UND", "UNIDAD_X_PAQUETE": 800, "UNIDAD_X_CAJA": 24},

    {"COD_PRODUCTO": "FKSHMA0800_12", "DESCRIPCION": "SHAMPOO FRESKITOS MANZANILLA X 800 ML / CAJA X 12 UND", "UNIDAD_X_PAQUETE": 800, "UNIDAD_X_CAJA": 12},

    {"COD_PRODUCTO": "FKSHRM0500", "DESCRIPCION": "SHAMPOO FRESKITOS ROMERO Y FRUTOS DEL BOSQUE X 500 ML / CAJA X 24", "UNIDAD_X_PAQUETE": 500, "UNIDAD_X_CAJA": 24},

    {"COD_PRODUCTO": "FKSHRM0800", "DESCRIPCION": "SHAMPOO FRESKITOS ROMERO Y FRUTOS DEL BOSQUE X 800 ML / CAJA X 12", "UNIDAD_X_PAQUETE": 800, "UNIDAD_X_CAJA": 12},

    # JABON FACE CLEAN CARBÓN ACTIVADO 75 GR is now primarily in unidades list.

    # JABON BAÑO BARRA CAJA SURTIDA X 75 GR is now primarily in unidades list.

    {"COD_PRODUCTO": "#N/D_PAÑAL0X18", "DESCRIPCION": "PAÑALES 0 X 18 / CAJA X 12", "UNIDAD_X_PAQUETE": 18, "UNIDAD_X_CAJA": 12},

    {"COD_PRODUCTO": "#N/D_PAÑAL1X18", "DESCRIPCION": "PAÑALES 1 X 18 / CAJA X 12", "UNIDAD_X_PAQUETE": 18, "UNIDAD_X_CAJA": 12},

    {"COD_PRODUCTO": "#N/D_PAÑAL2X18", "DESCRIPCION": "PAÑALES ET 2 X 18 / CAJA X 12", "UNIDAD_X_PAQUETE": 18, "UNIDAD_X_CAJA": 12},

    {"COD_PRODUCTO": "#N/D_PAÑAL3X18", "DESCRIPCION": "PAÑALES ET 3 X 18 / CAJA X 12", "UNIDAD_X_PAQUETE": 18, "UNIDAD_X_CAJA": 12},

    {"COD_PRODUCTO": "#N/D_PAÑAL4X18", "DESCRIPCION": "PAÑALES ET 4 X 18 / CAJA X 12", "UNIDAD_X_PAQUETE": 18, "UNIDAD_X_CAJA": 12},

    {"COD_PRODUCTO": "#N/D_TOC80", "DESCRIPCION": "TOALLAS DE COCINA 80 UNID / CAJA X 15", "UNIDAD_X_PAQUETE": 80, "UNIDAD_X_CAJA": 15},

    {"COD_PRODUCTO": "HCTHFL0020", "DESCRIPCION": "TOALLAS MULTIUSOS BBQ HYPER CLEAN X 20 / CAJA X 12 UND", "UNIDAD_X_PAQUETE": 20, "UNIDAD_X_CAJA": 12},

    # BOMBILLO LED POLAR X 7W and X 9W are now primarily in unidades list.

]



# NEW LIST: Products primarily sold by individual units or fixed small packs

# These are the products you explicitly listed for the "unidades" list.

# I've used their original codes where available and added '_UNIDAD' suffix to descriptions

# and sometimes to codes to differentiate them if they exist in both forms.

productos_data_unidades = [

    # Assuming 'UNIDAD' means a single item, not a pack of 10 for Dermadiva

    {"COD_PRODUCTO": "DDPHCO0010_U", "DESCRIPCION": "DERMADIVA CON COLAGENO / UNIDAD", "UNIDAD_X_PAQUETE": 1, "UNIDAD_X_CAJA": 480}, # Assuming a large box of individual units (48 cases * 10 units/case = 480 units per master box)

    {"COD_PRODUCTO": "DDPHPE0001_U", "DESCRIPCION": "DERMADIVA CON PEPINO / UNIDAD", "UNIDAD_X_PAQUETE": 1, "UNIDAD_X_CAJA": 480},

    {"COD_PRODUCTO": "DDPHSR0010_U", "DESCRIPCION": "DERMADIVA CON ROSAS Y ALOE VERA / UNIDAD", "UNIDAD_X_PAQUETE": 1, "UNIDAD_X_CAJA": 480},

    {"COD_PRODUCTO": "DDPHBA0010_U", "DESCRIPCION": "TOALLA DESMAQUILLANTE DERMADIVA / UNIDAD", "UNIDAD_X_PAQUETE": 1, "UNIDAD_X_CAJA": 480}, # Assuming 48 cases * 10 units/case = 480 units per master box

    

    # Amarre Toallas - Original was 'X 30 / CAJA X 24'. If this means individual 'paquete' of 30, then 'UNIDAD_X_PAQUETE' is 30, and 'UNIDAD_X_CAJA' is 24 (packs per box).

    # If '/ UNIDAD' means single wipe, that's a different product. I'll assume '/ UNIDAD' refers to the 'pack of 30'.

    {"COD_PRODUCTO": "#N/D_AMTOCOL_U", "DESCRIPCION": "AMARRE TO. DESMAQUILLANTES FACE CLEAN COLAGENO / UNIDAD", "UNIDAD_X_PAQUETE": 30, "UNIDAD_X_CAJA": 24}, # Assuming 'UNIDAD' refers to the 30-pack.

    {"COD_PRODUCTO": "#N/D_AMTOMIX_U", "DESCRIPCION": "AMARRE TO. DESMAQUILLANTES FACE CLEAN MIXTA / UNIDAD", "UNIDAD_X_PAQUETE": 30, "UNIDAD_X_CAJA": 24},

    {"COD_PRODUCTO": "#N/D_AMTOPEP_U", "DESCRIPCION": "AMARRE TO. DESMAQUILLANTES FACE CLEAN PEPINO / UNIDAD", "UNIDAD_X_PAQUETE": 30, "UNIDAD_X_CAJA": 24},

    {"COD_PRODUCTO": "#N/D_AMTORO_U", "DESCRIPCION": "AMARRE TO. DESMAQUILLANTES FACE CLEAN ROSAS Y ALOE VERA / UNIDAD", "UNIDAD_X_PAQUETE": 30, "UNIDAD_X_CAJA": 24},

    

    # Seniors Wipes - Original was 'X 50 / CAJA X 12'. Assuming '/ UNIDAD' refers to the 50-pack.

    {"COD_PRODUCTO": "SWPHSA0050_U", "DESCRIPCION": "TOALLAS HUMEDAS SENIORS WIPES / UNIDAD", "UNIDAD_X_PAQUETE": 50, "UNIDAD_X_CAJA": 12},



    # Pañitos Freskitos - Original varied (X10, X25, X40, X102, X105).

    # This implies selling individual packs, not individual wipes. So UNIDAD_X_PAQUETE is the pack size.

    {"COD_PRODUCTO": "FKPHSA0010_U", "DESCRIPCION": "PAÑITOS HÚMEDOS FRESKITOS X 10 / UNIDAD", "UNIDAD_X_PAQUETE": 10, "UNIDAD_X_CAJA": 48}, # Assumed specific pack size

    {"COD_PRODUCTO": "FKPHSA0025_U", "DESCRIPCION": "PAÑITOS HÚMEDOS FRESKITOS X 25 / UNIDAD", "UNIDAD_X_PAQUETE": 25, "UNIDAD_X_CAJA": 48},

    {"COD_PRODUCTO": "FTPHSA0040_U", "DESCRIPCION": "PAÑITOS HÚMEDOS FRESKITOS X 40 / UNIDAD", "UNIDAD_X_PAQUETE": 40, "UNIDAD_X_CAJA": 36},

    {"COD_PRODUCTO": "FTPHSA0102_U", "DESCRIPCION": "PAÑITOS HÚMEDOS FRESKITOS X 102 / UNIDAD", "UNIDAD_X_PAQUETE": 102, "UNIDAD_X_CAJA": 12},

    {"COD_PRODUCTO": "FTPHSA0105_U", "DESCRIPCION": "PAÑITOS HÚMEDOS FRESKITOS X 105 / UNIDAD", "UNIDAD_X_PAQUETE": 105, "UNIDAD_X_CAJA": 24},

    

    # Pañitos Húmedos ED Especial Negro - Original varied (X1, X10, X15).

    # '/ UNIDAD' for X1 implies truly single items, so UNIDAD_X_PAQUETE = 1, UNIDAD_X_CAJA = 480 (master carton of singles)

    {"COD_PRODUCTO": "FGPHSA001", "DESCRIPCION": "PAÑITOS HÚMEDOS ED ESPECIAL NEGRO / UNIDAD", "UNIDAD_X_PAQUETE": 1, "UNIDAD_X_CAJA": 480},



    # Detergente Maxi Wash Plus / Multiusos - Original by KG. '/ UNIDAD' implies selling a single unit of 5KG, 2KG, 1KG.

    {"COD_PRODUCTO": "#N/D_DMWP5KG_U", "DESCRIPCION": "DETERGENTE MAXI WASH PLUS X 5 KG / UNIDAD", "UNIDAD_X_PAQUETE": 5, "UNIDAD_X_CAJA": 4},

    {"COD_PRODUCTO": "#N/D_DMWP2KG_U", "DESCRIPCION": "DETERGENTE MAXI WASH PLUS X 2 KG / UNIDAD", "UNIDAD_X_PAQUETE": 2, "UNIDAD_X_CAJA": 10},

    {"COD_PRODUCTO": "MWHTAO1000_U", "DESCRIPCION": "DETERGENTE MAXI WASH PLUS X 1 KG / UNIDAD", "UNIDAD_X_PAQUETE": 1, "UNIDAD_X_CAJA": 20},

    {"COD_PRODUCTO": "#N/D_DMWMA1KG_U", "DESCRIPCION": "DETERGENTE MAXI WASH MULTIUSOS X 1 KG / UNIDAD", "UNIDAD_X_PAQUETE": 1, "UNIDAD_X_CAJA": 20},

    {"COD_PRODUCTO": "#N/D_DMWMA2KG_U", "DESCRIPCION": "DETERGENTE MAXI WASH MULTIUSOS X 2 KG / UNIDAD", "UNIDAD_X_PAQUETE": 2, "UNIDAD_X_CAJA": 10},



    # Enjuague Bucal Activmint - Original by ML. '/ UNIDAD' implies selling a single bottle.

    {"COD_PRODUCTO": "ANEBMF0300_U", "DESCRIPCION": "ENJUAGUE BUCAL ACTIVMINT MENTA FRESCA X 300ML / UNIDAD", "UNIDAD_X_PAQUETE": 300, "UNIDAD_X_CAJA": 15},

    {"COD_PRODUCTO": "#N/D_EBMF500_U", "DESCRIPCION": "ENJUAGUE BUCAL ACTIVMINT MENTA FRESCA X 500ML / UNIDAD", "UNIDAD_X_PAQUETE": 500, "UNIDAD_X_CAJA": 15},

    {"COD_PRODUCTO": "ANEBYB0300_U", "DESCRIPCION": "ENJUAGUE BUCAL ACTIVMINT YERBABUENA 300ML / UNIDAD", "UNIDAD_X_PAQUETE": 300, "UNIDAD_X_CAJA": 15},

    {"COD_PRODUCTO": "#N/D_EBYB500_U", "DESCRIPCION": "ENJUAGUE BUCAL ACTIVMINT YERBABUENA 500ML / UNIDAD", "UNIDAD_X_PAQUETE": 500, "UNIDAD_X_CAJA": 15},



    # Crema Humectante Freskitos - Original X 800ML. '/ UNIDAD' implies selling a single bottle.

    {"COD_PRODUCTO": "FKCRLB0012_U", "DESCRIPCION": "CREMA HUMECTANTE FRESKITOS MANOS Y CUERPO X 800ML / UNIDAD", "UNIDAD_X_PAQUETE": 800, "UNIDAD_X_CAJA": 12},



    # Jabon Liquido - Original X 1000ML/1L. '/ UNIDAD' implies selling a single bottle.

    {"COD_PRODUCTO": "#N/D_JLAB1000_U", "DESCRIPCION": "JABON LIQUIDO AVENA X 1000 ML / UNIDAD", "UNIDAD_X_PAQUETE": 1000, "UNIDAD_X_CAJA": 16},

    {"COD_PRODUCTO": "FKJLFR1000_U", "DESCRIPCION": "JABON LIQUIDO FRESKITOS FRUTOS ROJOS X 1L / UNIDAD", "UNIDAD_X_PAQUETE": 1000, "UNIDAD_X_CAJA": 16},

    {"COD_PRODUCTO": "FKJLMV1000_U", "DESCRIPCION": "JABON LIQUIDO FRESKITOS MANZANA VERDE X 1L / UNIDAD", "UNIDAD_X_PAQUETE": 1000, "UNIDAD_X_CAJA": 16},



    # Pañitos Humedos Freskipets - Original X 50. '/ UNIDAD' implies selling a single pack.

    {"COD_PRODUCTO": "FPPNMC050_U", "DESCRIPCION": "PAÑITOS HUMEDOS FRESKISPETS / UNIDAD", "UNIDAD_X_PAQUETE": 50, "UNIDAD_X_CAJA": 48},



    # Shampoo Freskitos - Original by ML. '/ UNIDAD' implies selling a single bottle.

    {"COD_PRODUCTO": "FKSHAL0800_U", "DESCRIPCION": "SHAMPOO FRESKITOS ALOE Y MANZANA X 500 ML / UNIDAD", "UNIDAD_X_PAQUETE": 500, "UNIDAD_X_CAJA": 24},

    {"COD_PRODUCTO": "FKSHMA0800_U", "DESCRIPCION": "SHAMPOO FRESKITOS MANZANILLA X 800 ML / UNIDAD", "UNIDAD_X_PAQUETE": 800, "UNIDAD_X_CAJA": 12}, # Picked the 12-unit case for simplicity here for the 'unit' sale.

    {"COD_PRODUCTO": "FKSHRM0500_U", "DESCRIPCION": "SHAMPOO FRESKITOS ROMERO Y FRUTOS DEL BOSQUE X 500 ML / UNIDAD", "UNIDAD_X_PAQUETE": 500, "UNIDAD_X_CAJA": 24},

    {"COD_PRODUCTO": "FKSHRM0800_U", "DESCRIPCION": "SHAMPOO FRESKITOS ROMERO Y FRUTOS DEL BOSQUE X 800 ML / UNIDAD", "UNIDAD_X_PAQUETE": 800, "UNIDAD_X_CAJA": 12},



    # Jabon Face Clean / Baño Barra - Original by GR. '/ UNIDAD' implies selling a single bar.

    {"COD_PRODUCTO": "#N/D_JBCA75_U", "DESCRIPCION": "JABON FACE CLEAN CARBÓN ACTIVADO 75 GR / UNIDAD", "UNIDAD_X_PAQUETE": 1, "UNIDAD_X_CAJA": 18}, # 1 unit = 1 bar, 18 bars per box

    {"COD_PRODUCTO": "#N/D_JBSC75_U", "DESCRIPCION": "JABON BAÑO BARRA CAJA SURTIDA X 75 GR / UNIDAD", "UNIDAD_X_PAQUETE": 1, "UNIDAD_X_CAJA": 75}, # 1 unit = 1 bar, 75 bars per box



    # Pañales - Original X 18. '/ UNIDAD' implies selling a single pack of 18.

    {"COD_PRODUCTO": "#N/D_PAÑAL0X18_U", "DESCRIPCION": "PAÑALES ET 0 X 18 / UNIDAD", "UNIDAD_X_PAQUETE": 18, "UNIDAD_X_CAJA": 12},

    {"COD_PRODUCTO": "#N/D_PAÑAL1X18_U", "DESCRIPCION": "PAÑALES ET 1 X 18 / UNIDAD", "UNIDAD_X_PAQUETE": 18, "UNIDAD_X_CAJA": 12},

    {"COD_PRODUCTO": "#N/D_PAÑAL2X18_U", "DESCRIPCION": "PAÑALES ET 2 X 18 / UNIDAD", "UNIDAD_X_PAQUETE": 18, "UNIDAD_X_CAJA": 12},

    {"COD_PRODUCTO": "#N/D_PAÑAL3X18_U", "DESCRIPCION": "PAÑALES ET 3 X 18 / UNIDAD", "UNIDAD_X_PAQUETE": 18, "UNIDAD_X_CAJA": 12},

    {"COD_PRODUCTO": "#N/D_PAÑAL4X18_U", "DESCRIPCION": "PAÑALES ET 4 X 18 / UNIDAD", "UNIDAD_X_PAQUETE": 18, "UNIDAD_X_CAJA": 12},



    # Toallas de Cocina - Original 80 UNID. '/ UNIDAD' implies selling a single roll.

    {"COD_PRODUCTO": "#N/D_TOC80_U", "DESCRIPCION": "TOALLAS DE COCINA 80 UNID / UNIDAD", "UNIDAD_X_PAQUETE": 80, "UNIDAD_X_CAJA": 15},



    # Toallas Multiusos BBQ - Original X 20. '/ UNIDAD' implies selling a single pack of 20.

    {"COD_PRODUCTO": "HCTHFL0020_U", "DESCRIPCION": "TOALLAS MULTIUSOS BBQ HYPER CLEAN / UNIDAD", "UNIDAD_X_PAQUETE": 20, "UNIDAD_X_CAJA": 12},



    # Bombillo LED Polar - Original X 7W, X 9W. '/ UNIDAD' implies selling a single bulb.

    {"COD_PRODUCTO": "POBOLD7W_U", "DESCRIPCION": "BOMBILLO LED POLAR X 7W / UNIDAD", "UNIDAD_X_PAQUETE": 1, "UNIDAD_X_CAJA": 12}, # 1 unit = 1 bulb, 12 bulbs per box

    {"COD_PRODUCTO": "#N/D_BLP9W_U", "DESCRIPCION": "BOMBILLO LED POLAR X 9W / UNIDAD", "UNIDAD_X_PAQUETE": 1, "UNIDAD_X_CAJA": 12},

]



df_productos_cajas = pd.DataFrame(productos_data_cajas)

df_productos_unidades = pd.DataFrame(productos_data_unidades)



# Prepend an empty string to the product descriptions for the "empty" selectbox option

all_product_options_cajas = [""] + df_productos_cajas['DESCRIPCION'].tolist()

all_product_options_unidades = [""] + df_productos_unidades['DESCRIPCION'].tolist()





# --- Initialize session state ---

if 'pedido_actual' not in st.session_state:

    st.session_state.pedido_actual = []

if 'global_summary_core_text' not in st.session_state:

    st.session_state.global_summary_core_text = ""

if 'show_generated_summary' not in st.session_state:

    st.session_state.show_generated_summary = False

if 'cliente_email_input' not in st.session_state:

    st.session_state.cliente_email_input = ''

if 'cliente_telefono_input' not in st.session_state:

    st.session_state.cliente_telefono_input = ''



# State for selected product type (to control which selectbox is active)

if 'selected_product_type' not in st.session_state:

    st.session_state.selected_product_type = "cajas" # Default to 'cajas' or 'unidades'



# State for selectbox index and quantities for *each* product type

if 'product_select_index_cajas' not in st.session_state:

    st.session_state.product_select_index_cajas = 0

if 'cantidad_cajas_input' not in st.session_state:

    st.session_state.cantidad_cajas_input = 0



if 'product_select_index_unidades' not in st.session_state:

    st.session_state.product_select_index_unidades = 0

if 'cantidad_unidades_input' not in st.session_state:

    st.session_state.cantidad_unidades_input = 0



if 'current_consecutive_number' not in st.session_state:

    st.session_state.current_consecutive_number = None

if 'reset_inputs_flag' not in st.session_state:

    st.session_state.reset_inputs_flag = False



# --- NEW: Check reset flag at the start of the script ---

if st.session_state.reset_inputs_flag:

    # Only reset the quantities, not the selectbox index unless it's explicitly cleared

    st.session_state.cantidad_cajas_input = 0

    st.session_state.cantidad_unidades_input = 0

    st.session_state.reset_inputs_flag = False # Reset the flag immediately



# --- Validation functions for email and phone ---

def is_valid_email(email):

    """Basic email validation."""

    if not email: # Allow empty email

        return True

    return re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email)



def is_valid_phone(phone):

    """Basic phone validation (allows for optional leading + and spaces/hyphens)."""

    if not phone: # Allow empty phone

        return True

    # Ensures at least 7 digits, allows + at start, and spaces/hyphens in between

    return re.match(r"^\+?[\d\s\-]{7,15}$", phone)



# --- Callback function to handle adding product and setting reset flag ---

def add_product_callback(producto_encontrado, selected_description, cantidad_cajas, cantidad_unidades, product_type):

    if not selected_description or (cantidad_cajas == 0 and cantidad_unidades == 0):

        st.error("❌ Error: Selecciona un producto e ingresa al menos una cantidad (caja o unidad).")

    else:

        if product_type == "cajas":

            # For 'cajas' list, UNIDAD_X_PAQUETE is the units in one package, UNIDAD_X_CAJA is packages per box

            # Total units = (Cajas * UNIDAD_X_CAJA * UNIDAD_X_PAQUETE) + (Individual Units)

            unidades_por_paquete_en_caja = producto_encontrado['UNIDAD_X_PAQUETE']

            paquetes_por_caja = producto_encontrado['UNIDAD_X_CAJA']

            total_calc_units = (cantidad_cajas * paquetes_por_caja * unidades_por_paquete_en_caja) + cantidad_unidades



            st.session_state.pedido_actual.append({

                "COD_PRODUCTO": producto_encontrado['COD_PRODUCTO'],

                "DESCRIPCION": selected_description,

                "TIPO_PEDIDO": "Por Cajas/Bultos",

                "CANT_CAJAS": cantidad_cajas,

                "CANT_UNIDADES_IND": cantidad_unidades, # These are extra individual units (from a package)

                "UNIDAD_X_PAQUETE_EN_CAJA": unidades_por_paquete_en_caja,

                "PAQUETES_X_CAJA": paquetes_por_caja,

                "TOTAL_UNIDADES_CALCULADAS": total_calc_units

            })

        elif product_type == "unidades":

            # For 'unidades' list, UNIDAD_X_PAQUETE is the base unit being sold (e.g., 1 bulb, 1 pack of 30 wipes)

            # And UNIDAD_X_CAJA is how many of those base units come in a larger case of units.

            

            # Total units = (Cajas_de_unidades * UNIDAD_X_CAJA * UNIDAD_X_PAQUETE) + (Individual_Units * UNIDAD_X_PAQUETE)

            unidad_base_producto_valor = producto_encontrado['UNIDAD_X_PAQUETE']

            unidades_por_caja_de_unidad = producto_encontrado['UNIDAD_X_CAJA']

            

            total_calc_units = (cantidad_cajas * unidades_por_caja_de_unidad * unidad_base_producto_valor) + \

                               (cantidad_unidades * unidad_base_producto_valor)



            st.session_state.pedido_actual.append({

                "COD_PRODUCTO": producto_encontrado['COD_PRODUCTO'],

                "DESCRIPCION": selected_description,

                "TIPO_PEDIDO": "Por Unidades/Packs",

                "CANT_CAJAS": cantidad_cajas, # These are 'boxes of individual units/packs'

                "CANT_UNIDADES_IND": cantidad_unidades, # These are truly individual units (e.g., single bulb) or individual packs (e.g., 30-wipe pack)

                "UNIDAD_BASE_PRODUCTO": unidad_base_producto_valor,

                "UNIDADES_POR_CAJA_DE_UNIDAD": unidades_por_caja_de_unidad,

                "TOTAL_UNIDADES_CALCULADAS": total_calc_units

            })

        

        st.success(f"Producto '{selected_description}' añadido al pedido.")

        st.session_state.global_summary_core_text = ""

        st.session_state.show_generated_summary = False

        st.session_state.reset_inputs_flag = True # Set the flag here to trigger reset on next run

        # No need for st.rerun() here, as setting the flag will cause it naturally



# --- Callback function for 'Volver y Añadir Más Productos' button ---

def go_back_and_add_more():

    st.session_state.show_generated_summary = False

    st.session_state.global_summary_core_text = ""

    st.session_state.reset_inputs_flag = True # Reset inputs when going back

    # No st.rerun() needed



# --- Callback function for 'Limpiar Pedido Completo' button ---

def clear_all_products():

    st.session_state.pedido_actual = []

    st.session_state.global_summary_core_text = ""

    st.session_state.show_generated_summary = False

    st.session_state.current_consecutive_number = None

    st.session_state.reset_inputs_flag = True # Reset inputs when clearing order

    st.success("✔️ ¡Pedido limpiado!")

    # No st.rerun() needed





# --- Streamlit UI ---

st.set_page_config(layout="centered", page_title="Generador de Pedidos Consumidor Final")



# --- Sección para el logo ---

try:

    st.image("LOGO 2.png", width=200)

except FileNotFoundError:

    st.warning("⚠️ No se encontró el logo. Asegúrate de que 'LOGO 2.png' esté en la misma carpeta o la ruta sea correcta.")



st.title("📝 Generador de Pedidos Consumidor Final")

st.markdown("Completa los detalles para generar un resumen de tu solicitud.")



st.write("---")



st.subheader("Datos del Cliente")

nit = st.text_input("NIT:", value='222222222', disabled=True, key='nit_input')

nombre_cliente = st.text_input("Cliente:", value='CONSUMIDOR FINAL', disabled=True, key='cliente_input')



st.write("---")



st.subheader("Selección de Productos")



if not st.session_state.show_generated_summary:

    # Use radio buttons to select which list to show

    selected_product_type_ui = st.radio(

        "Seleccionar tipo de producto:",

        options=["Por Cajas/Bultos", "Por Unidades/Packs"],

        index=0 if st.session_state.selected_product_type == "cajas" else 1,

        key='product_type_selector_radio'

    )



    # Update session state based on radio button

    if selected_product_type_ui == "Por Cajas/Bultos":

        st.session_state.selected_product_type = "cajas"

    else:

        st.session_state.selected_product_type = "unidades"

    

    selected_description = ""

    producto_encontrado = None

    cantidad_cajas_val = st.session_state.cantidad_cajas_input

    cantidad_unidades_val = st.session_state.cantidad_unidades_input



    if st.session_state.selected_product_type == "cajas":

        selected_description = st.selectbox(

            'Selecciona un producto (Por Cajas/Bultos):',

            options=all_product_options_cajas,

            index=st.session_state.product_select_index_cajas,

            key='product_select_widget_cajas',

            help="Empieza a escribir o selecciona un producto de la lista para ordenar por cajas."

        )

        if selected_description:

            # Update the index only if a valid selection is made, not on initial empty state

            if selected_description in all_product_options_cajas:

                st.session_state.product_select_index_cajas = all_product_options_cajas.index(selected_description)

            else:

                st.session_state.product_select_index_cajas = 0 # Reset to empty if invalid somehow



            df_filtered = df_productos_cajas[df_productos_cajas['DESCRIPCION'] == selected_description]

            if not df_filtered.empty:

                producto_encontrado = df_filtered.iloc[0]

                st.info(f"Unidades por paquete: {producto_encontrado['UNIDAD_X_PAQUETE']}, Paquetes por caja: {producto_encontrado['UNIDAD_X_CAJA']}")

            else:

                st.error("Producto no válido o no encontrado en la lista de cajas. Por favor, selecciona de la lista.")



        col1, col2 = st.columns(2)

        with col1:

            cantidad_cajas_val = st.number_input(

                "Cantidad de Cajas:",

                min_value=0,

                value=st.session_state.cantidad_cajas_input,

                step=1,

                disabled=(producto_encontrado is None),

                key='cantidad_cajas_input' # Reusing key, but it's fine since it's inside conditional block

            )

        with col2:

            cantidad_unidades_val = st.number_input(

                "Cantidad de Unidades Individuales Adicionales:",

                min_value=0,

                value=st.session_state.cantidad_unidades_input,

                step=1,

                disabled=(producto_encontrado is None),

                key='cantidad_unidades_input_cajas_extra'

            )



    elif st.session_state.selected_product_type == "unidades":

        selected_description = st.selectbox(

            'Selecciona un producto (Por Unidades/Packs):',

            options=all_product_options_unidades,

            index=st.session_state.product_select_index_unidades,

            key='product_select_widget_unidades',

            help="Empieza a escribir o selecciona un producto de la lista para ordenar por unidades."

        )

        if selected_description:

            # Update the index only if a valid selection is made

            if selected_description in all_product_options_unidades:

                st.session_state.product_select_index_unidades = all_product_options_unidades.index(selected_description)

            else:

                st.session_state.product_select_index_unidades = 0 # Reset to empty if invalid somehow



            df_filtered = df_productos_unidades[df_productos_unidades['DESCRIPCION'] == selected_description]

            if not df_filtered.empty:

                producto_encontrado = df_filtered.iloc[0]

                st.info(f"Unidad base del producto: {producto_encontrado['UNIDAD_X_PAQUETE']}, Unidades por caja de este producto: {producto_encontrado['UNIDAD_X_CAJA']}")

            else:

                st.error("Producto no válido o no encontrado en la lista de unidades. Por favor, selecciona de la lista.")



        col1, col2 = st.columns(2)

        with col1:

            cantidad_cajas_val = st.number_input(

                "Cantidad de Cajas (de estas unidades/packs):",

                min_value=0,

                value=st.session_state.cantidad_cajas_input,

                step=1,

                disabled=(producto_encontrado is None),

                key='cantidad_cajas_input_unidades'

            )

        with col2:

            cantidad_unidades_val = st.number_input(

                "Cantidad de Unidades Individuales/Packs:",

                min_value=0,

                value=st.session_state.cantidad_unidades_input,

                step=1,

                disabled=(producto_encontrado is None),

                key='cantidad_unidades_input_unidades'

            )



    st.button(

        'Añadir Producto al Pedido',

        type="primary",

        key='add_product_button',

        disabled=(producto_encontrado is None or (cantidad_cajas_val == 0 and cantidad_unidades_val == 0)),

        on_click=add_product_callback,

        args=(producto_encontrado, selected_description, cantidad_cajas_val, cantidad_unidades_val, st.session_state.selected_product_type)

    )



st.write("---")



st.subheader("Productos en el Pedido")

if st.session_state.pedido_actual:

    if not st.session_state.show_generated_summary:

        st.button("Limpiar Pedido Completo", key='clear_all_products_button', type="secondary", on_click=clear_all_products)

            

    for i, item in enumerate(st.session_state.pedido_actual):

        if item["TIPO_PEDIDO"] == "Por Cajas/Bultos":

            st.markdown(f"**{i+1}.** {item['DESCRIPCION']} - Cajas: {item['CANT_CAJAS']}, Unidades Adic.: {item['CANT_UNIDADES_IND']} (Total Calculado: {item['TOTAL_UNIDADES_CALCULADAS']} uds)")

        elif item["TIPO_PEDIDO"] == "Por Unidades/Packs":

            st.markdown(f"**{i+1}.** {item['DESCRIPCION']} - Cajas (de uds/packs): {item['CANT_CAJAS']}, Unidades/Packs: {item['CANT_UNIDADES_IND']} (Total Calculado: {item['TOTAL_UNIDADES_CALCULADAS']} uds)")

else:

    st.info("No hay productos añadidos al pedido aún.")



st.write("---")



st.subheader("Información de Contacto Adicional")



cliente_email_input = st.text_input("Email Cliente:", value=st.session_state.cliente_email_input, placeholder='ejemplo@dominio.com', key='cliente_email_input')

cliente
        
st.markdown("---")
st.caption("Hecho por Cartera ATW Internacional.")
