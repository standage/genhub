-- generic checks
has_accession = function(feature)
    it("has an accession", function()
        expect(feature:get_attribute("accession")).should_not_be(nil)
    end)
end

encompasses_children = function(feature)
    it("encompasses all subfeatures", function()
        for child in feature:children() do
            expect(feature:get_range():contains(child:get_range())).should_be(true)
        end
    end)
end

-- feature-specific checks
describe.feature("gene", function(gene)
    has_accession(gene)
    encompasses_children(gene)

    it("is top-level feature", function()
        expect(gene:appears_as_root_node()).should_be(true)
    end)
end)

describe.feature("mRNA", function(mrna)
    has_accession(mrna)
    encompasses_children(mrna)

    it("associated with a gene feature", function()
        expect(mrna:appears_as_child_of_type("gene")).should_be(true)
    end)

    it("has no explicitly defined introns", function()
        expect(mrna:has_child_of_type("intron")).should_be(false)
    end)

    it("has a single coding sequence", function()
        expect(mrna:has_child_of_type("CDS")).should_be(true)
        cds = mrna:children_of_type("CDS")
        cdsid = nil
        consistent = true
        for cexon in cds do
            if cdsid == nil then
                cdsid = cexon:get_attribute("ID")
            else
                consistent = consistent and cexon:get_attribute("ID") == cdsid
            end
        end
        expect(consistent).should_be(true)
    end)
end)
