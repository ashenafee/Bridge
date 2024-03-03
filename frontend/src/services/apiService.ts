interface Identifiers {
    txid: string;
    gene_id: string;
    nuc_id: string;
}

/**
 * Retrieves the identifiers of all species under a taxonomy that have a given
 * gene available on the NCBI database.
 * 
 * @param taxonName - The taxon name.
 * @param geneName - The gene name.
 * @param speciesMap - A map of species identifiers.
 * @returns A promise that resolves to an array of species objects, each containing the species name and identifiers.
 * @throws An error if the network response is not ok.
 */
export const getSpecies = async (taxonName: string, geneName: string, speciesMap: { [key: string]: string }): Promise<{ name: string, identifiers: Identifiers[] }[]> => {
    const response = await fetch("http://localhost:8000/api/get_species", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            taxonName,
            geneName,
        }),
    });

    if (!response.ok) {
        throw new Error("Network response was not ok");
    }

    const data = await response.json();
    const species = data.species_ids;

    return Object.entries(species).map(([name, identifiers]: [string, unknown]) => {

        // Cast the identifiers to the Identifiers type
        const typedIdentifiers = identifiers as Identifiers[];

        // Add {txid: name} to the speciesMap if that txid is not already in the map
        typedIdentifiers.forEach((identifier: Identifiers) => {
            if (!(identifier.txid in speciesMap)) {
                speciesMap[identifier.txid] = name;
            }
        });

        return {
            name,
            identifiers: identifiers as Identifiers[]
        };
    });
};

/**
 * Downloads the coding sequences for provided nucleotide sequences identifiers
 * from the NCBI database.
 * 
 * @param speciesSubset - An object containing species identifiers.
 * @returns A Promise that resolves to the downloaded data.
 * @throws An error if the network response is not ok.
 */
export const downloadSpecies = async (speciesSubset: { [key: string]: Identifiers[] }) => {
    const response = await fetch("http://localhost:8000/api/download", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            species_data: speciesSubset
        }),
    });

    if (!response.ok) {
        throw new Error("Network response was not ok");
    }

    const data = await response.json();
    return data;
};