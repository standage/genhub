describe.feature("locus", function(locus)
    it("is classified correctly", function()
        local locus_type = locus:get_attribute("iLocus_type")
        expect(locus_type).should_not_be(nil)
        if (locus_type ~= nil) then
            if (locus_type == "iiLocus" or locus_type == "fiLocus") then
                expect(locus:has_child_of_type("gene")).should_be(false)
            elseif (locus_type == "siLocus") then
                iter = gt.feature_node_iterator_new_direct(locus)
                child = iter:next()
                nextchild = iter:next()
                expect(nextchild).should_be(nil)
                expect(child:get_type()).should_be("gene")
                expect(child:has_child_of_type("mRNA")).should_be(true)
            elseif (locus_type == "niLocus") then
                expect(locus:has_child_of_supertype("transcript")).should_be(true)
                expect(locus:has_child_of_type("mRNA")).should_be(false)
            elseif (locus_type == "ciLocus") then
                iter = gt.feature_node_iterator_new_direct(locus)
                child = iter:next()
                genecount = 0
                while not(child == nil) do
                    if(child:get_type() == "gene") then
                        genecount = genecount + 1
                    end
                    child = iter:next()
                end
                expect(genecount).should_be_larger_than(1)
            end
        end
    end)
end)
